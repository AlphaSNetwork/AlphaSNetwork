#![cfg_attr(not(feature = "std"), no_std)]

use ink::prelude::vec::Vec;
use ink::prelude::string::String;

#[ink::contract]
mod voting_contract {
    use ink::storage::Mapping;
    use ink::prelude::vec::Vec;
    use ink::prelude::string::String;

    /// Defines the storage of your contract.
    #[ink(storage)]
    pub struct VotingContract {
        /// The contract owner
        owner: AccountId,
        /// Mapping from poll ID to poll data
        polls: Mapping<u32, Poll>,
        /// Next available poll ID
        next_poll_id: u32,
        /// Mapping from (poll_id, voter) to vote
        votes: Mapping<(u32, AccountId), Vote>,
        /// Mapping from poll_id to voter list
        poll_voters: Mapping<u32, Vec<AccountId>>,
    }

    /// Poll structure
    #[derive(scale::Decode, scale::Encode)]
    #[cfg_attr(
        feature = "std",
        derive(scale_info::TypeInfo, ink::storage::traits::StorageLayout)
    )]
    pub struct Poll {
        pub title: String,
        pub description: String,
        pub options: Vec<String>,
        pub creator: AccountId,
        pub start_time: u64,
        pub end_time: u64,
        pub is_active: bool,
        pub total_votes: u32,
    }

    /// Vote structure
    #[derive(scale::Decode, scale::Encode)]
    #[cfg_attr(
        feature = "std",
        derive(scale_info::TypeInfo, ink::storage::traits::StorageLayout)
    )]
    pub struct Vote {
        pub option_index: u32,
        pub timestamp: u64,
    }

    /// Poll results structure
    #[derive(scale::Decode, scale::Encode)]
    #[cfg_attr(
        feature = "std",
        derive(scale_info::TypeInfo)
    )]
    pub struct PollResults {
        pub poll_id: u32,
        pub title: String,
        pub option_votes: Vec<u32>,
        pub total_votes: u32,
        pub is_ended: bool,
    }

    /// Events emitted by the contract
    #[ink(event)]
    pub struct PollCreated {
        #[ink(topic)]
        poll_id: u32,
        #[ink(topic)]
        creator: AccountId,
        title: String,
    }

    #[ink(event)]
    pub struct VoteCast {
        #[ink(topic)]
        poll_id: u32,
        #[ink(topic)]
        voter: AccountId,
        option_index: u32,
    }

    #[ink(event)]
    pub struct PollEnded {
        #[ink(topic)]
        poll_id: u32,
        total_votes: u32,
    }

    /// Contract errors
    #[derive(scale::Decode, scale::Encode)]
    #[cfg_attr(
        feature = "std",
        derive(scale_info::TypeInfo)
    )]
    pub enum Error {
        /// Poll not found
        PollNotFound,
        /// Poll has ended
        PollEnded,
        /// Poll has not started
        PollNotStarted,
        /// Invalid option index
        InvalidOption,
        /// Already voted
        AlreadyVoted,
        /// Not authorized
        NotAuthorized,
        /// Invalid time range
        InvalidTimeRange,
        /// Empty options
        EmptyOptions,
    }

    pub type Result<T> = core::result::Result<T, Error>;

    impl VotingContract {
        /// Constructor that initializes the contract
        #[ink(constructor)]
        pub fn new() -> Self {
            Self {
                owner: Self::env().caller(),
                polls: Mapping::default(),
                next_poll_id: 1,
                votes: Mapping::default(),
                poll_voters: Mapping::default(),
            }
        }

        /// Create a new poll
        #[ink(message)]
        pub fn create_poll(
            &mut self,
            title: String,
            description: String,
            options: Vec<String>,
            duration_hours: u64,
        ) -> Result<u32> {
            if options.is_empty() {
                return Err(Error::EmptyOptions);
            }

            let caller = self.env().caller();
            let current_time = self.env().block_timestamp();
            let end_time = current_time + (duration_hours * 3600 * 1000); // Convert hours to milliseconds

            if end_time <= current_time {
                return Err(Error::InvalidTimeRange);
            }

            let poll_id = self.next_poll_id;
            
            let poll = Poll {
                title: title.clone(),
                description,
                options,
                creator: caller,
                start_time: current_time,
                end_time,
                is_active: true,
                total_votes: 0,
            };

            self.polls.insert(poll_id, &poll);
            self.poll_voters.insert(poll_id, &Vec::new());
            self.next_poll_id += 1;

            self.env().emit_event(PollCreated {
                poll_id,
                creator: caller,
                title,
            });

            Ok(poll_id)
        }

        /// Cast a vote for a poll
        #[ink(message)]
        pub fn vote(&mut self, poll_id: u32, option_index: u32) -> Result<()> {
            let caller = self.env().caller();
            let current_time = self.env().block_timestamp();

            let mut poll = self.polls.get(poll_id).ok_or(Error::PollNotFound)?;

            // Check if poll is active and within time range
            if !poll.is_active {
                return Err(Error::PollEnded);
            }

            if current_time < poll.start_time {
                return Err(Error::PollNotStarted);
            }

            if current_time > poll.end_time {
                return Err(Error::PollEnded);
            }

            // Check if option index is valid
            if option_index as usize >= poll.options.len() {
                return Err(Error::InvalidOption);
            }

            // Check if user has already voted
            if self.votes.contains((poll_id, caller)) {
                return Err(Error::AlreadyVoted);
            }

            // Record the vote
            let vote = Vote {
                option_index,
                timestamp: current_time,
            };

            self.votes.insert((poll_id, caller), &vote);

            // Add voter to poll voters list
            let mut voters = self.poll_voters.get(poll_id).unwrap_or_default();
            voters.push(caller);
            self.poll_voters.insert(poll_id, &voters);

            // Update poll total votes
            poll.total_votes += 1;
            self.polls.insert(poll_id, &poll);

            self.env().emit_event(VoteCast {
                poll_id,
                voter: caller,
                option_index,
            });

            Ok(())
        }

        /// End a poll (only creator can end)
        #[ink(message)]
        pub fn end_poll(&mut self, poll_id: u32) -> Result<()> {
            let caller = self.env().caller();
            let mut poll = self.polls.get(poll_id).ok_or(Error::PollNotFound)?;

            // Only creator or owner can end the poll
            if caller != poll.creator && caller != self.owner {
                return Err(Error::NotAuthorized);
            }

            poll.is_active = false;
            self.polls.insert(poll_id, &poll);

            self.env().emit_event(PollEnded {
                poll_id,
                total_votes: poll.total_votes,
            });

            Ok(())
        }

        /// Get poll information
        #[ink(message)]
        pub fn get_poll(&self, poll_id: u32) -> Option<Poll> {
            self.polls.get(poll_id)
        }

        /// Get poll results
        #[ink(message)]
        pub fn get_poll_results(&self, poll_id: u32) -> Result<PollResults> {
            let poll = self.polls.get(poll_id).ok_or(Error::PollNotFound)?;
            let voters = self.poll_voters.get(poll_id).unwrap_or_default();

            let mut option_votes = vec![0u32; poll.options.len()];

            // Count votes for each option
            for voter in voters.iter() {
                if let Some(vote) = self.votes.get((poll_id, *voter)) {
                    if (vote.option_index as usize) < option_votes.len() {
                        option_votes[vote.option_index as usize] += 1;
                    }
                }
            }

            let current_time = self.env().block_timestamp();
            let is_ended = !poll.is_active || current_time > poll.end_time;

            Ok(PollResults {
                poll_id,
                title: poll.title,
                option_votes,
                total_votes: poll.total_votes,
                is_ended,
            })
        }

        /// Check if user has voted for a poll
        #[ink(message)]
        pub fn has_voted(&self, poll_id: u32, voter: AccountId) -> bool {
            self.votes.contains((poll_id, voter))
        }

        /// Get user's vote for a poll
        #[ink(message)]
        pub fn get_user_vote(&self, poll_id: u32, voter: AccountId) -> Option<Vote> {
            self.votes.get((poll_id, voter))
        }

        /// Get total number of polls
        #[ink(message)]
        pub fn get_total_polls(&self) -> u32 {
            self.next_poll_id - 1
        }

        /// Get contract owner
        #[ink(message)]
        pub fn get_owner(&self) -> AccountId {
            self.owner
        }
    }

    /// Unit tests
    #[cfg(test)]
    mod tests {
        use super::*;

        #[ink::test]
        fn new_works() {
            let contract = VotingContract::new();
            assert_eq!(contract.get_total_polls(), 0);
        }

        #[ink::test]
        fn create_poll_works() {
            let mut contract = VotingContract::new();
            let title = "Test Poll".to_string();
            let description = "Test Description".to_string();
            let options = vec!["Option 1".to_string(), "Option 2".to_string()];
            
            let result = contract.create_poll(title.clone(), description, options, 24);
            assert!(result.is_ok());
            assert_eq!(result.unwrap(), 1);
            assert_eq!(contract.get_total_polls(), 1);

            let poll = contract.get_poll(1).unwrap();
            assert_eq!(poll.title, title);
            assert_eq!(poll.options.len(), 2);
        }

        #[ink::test]
        fn vote_works() {
            let mut contract = VotingContract::new();
            let title = "Test Poll".to_string();
            let description = "Test Description".to_string();
            let options = vec!["Option 1".to_string(), "Option 2".to_string()];
            
            let poll_id = contract.create_poll(title, description, options, 24).unwrap();
            let result = contract.vote(poll_id, 0);
            assert!(result.is_ok());

            let poll = contract.get_poll(poll_id).unwrap();
            assert_eq!(poll.total_votes, 1);
        }

        #[ink::test]
        fn cannot_vote_twice() {
            let mut contract = VotingContract::new();
            let title = "Test Poll".to_string();
            let description = "Test Description".to_string();
            let options = vec!["Option 1".to_string(), "Option 2".to_string()];
            
            let poll_id = contract.create_poll(title, description, options, 24).unwrap();
            let _ = contract.vote(poll_id, 0);
            let result = contract.vote(poll_id, 1);
            assert_eq!(result, Err(Error::AlreadyVoted));
        }
    }
}

