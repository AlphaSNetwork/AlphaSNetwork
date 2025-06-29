#![cfg_attr(not(feature = "std"), no_std)]

/// AlphaSocial pallet for advanced social features
/// 
/// This pallet implements advanced social networking features including:
/// - Group management and messaging
/// - Private messaging with encryption
/// - Content moderation and reporting
/// - User reputation system
/// - Advanced privacy controls

pub use pallet::*;

#[frame_support::pallet]
pub mod pallet {
    use frame_support::{
        dispatch::{DispatchResult, DispatchError},
        pallet_prelude::*,
        traits::{Get, Currency, ReservableCurrency, Randomness},
        PalletId,
    };
    use frame_system::pallet_prelude::*;
    use sp_std::vec::Vec;
    use sp_runtime::traits::{Saturating, Zero};
    use codec::{Encode, Decode};
    use scale_info::TypeInfo;

    #[pallet::pallet]
    #[pallet::generate_store(pub(super) trait Store)]
    pub struct Pallet<T>(_);

    /// Configure the pallet by specifying the parameters and types on which it depends.
    #[pallet::config]
    pub trait Config: frame_system::Config {
        /// Because this pallet emits events, it depends on the runtime's definition of an event.
        type RuntimeEvent: From<Event<Self>> + IsType<<Self as frame_system::Config>::RuntimeEvent>;

        /// The currency used for paying deposits and fees.
        type Currency: Currency<Self::AccountId> + ReservableCurrency<Self::AccountId>;

        /// Randomness source for generating group IDs and other random values.
        type Randomness: Randomness<Self::Hash, Self::BlockNumber>;

        /// The amount of currency needed to reserve for creating a group.
        #[pallet::constant]
        type GroupDeposit: Get<<Self::Currency as Currency<Self::AccountId>>::Balance>;

        /// Maximum number of members in a group.
        #[pallet::constant]
        type MaxGroupMembers: Get<u32>;

        /// Maximum length of group name.
        #[pallet::constant]
        type MaxGroupNameLength: Get<u32>;

        /// Maximum length of group description.
        #[pallet::constant]
        type MaxGroupDescriptionLength: Get<u32>;

        /// Maximum length of private message content.
        #[pallet::constant]
        type MaxMessageLength: Get<u32>;

        /// The pallet's id, used for deriving its sovereign account ID.
        #[pallet::constant]
        type PalletId: Get<PalletId>;
    }

    /// Group information structure
    #[derive(Encode, Decode, Clone, PartialEq, Eq, RuntimeDebug, TypeInfo)]
    pub struct GroupInfo<AccountId, Balance> {
        pub creator: AccountId,
        pub name: Vec<u8>,
        pub description: Vec<u8>,
        pub avatar_hash: Option<Vec<u8>>, // IPFS hash of group avatar
        pub member_count: u32,
        pub is_public: bool,
        pub created_at: u64,
        pub deposit: Balance,
    }

    /// Private message structure
    #[derive(Encode, Decode, Clone, PartialEq, Eq, RuntimeDebug, TypeInfo)]
    pub struct PrivateMessage<AccountId> {
        pub sender: AccountId,
        pub recipient: AccountId,
        pub content_hash: Vec<u8>, // IPFS hash of encrypted message
        pub timestamp: u64,
        pub is_read: bool,
    }

    /// Content report structure
    #[derive(Encode, Decode, Clone, PartialEq, Eq, RuntimeDebug, TypeInfo)]
    pub struct ContentReport<AccountId> {
        pub reporter: AccountId,
        pub target_account: Option<AccountId>,
        pub content_hash: Option<Vec<u8>>,
        pub reason: ReportReason,
        pub description: Vec<u8>,
        pub timestamp: u64,
        pub status: ReportStatus,
    }

    /// Report reason enumeration
    #[derive(Encode, Decode, Clone, PartialEq, Eq, RuntimeDebug, TypeInfo)]
    pub enum ReportReason {
        Spam,
        Harassment,
        InappropriateContent,
        Copyright,
        FakeNews,
        Other,
    }

    /// Report status enumeration
    #[derive(Encode, Decode, Clone, PartialEq, Eq, RuntimeDebug, TypeInfo)]
    pub enum ReportStatus {
        Pending,
        UnderReview,
        Resolved,
        Dismissed,
    }

    /// User reputation structure
    #[derive(Encode, Decode, Clone, PartialEq, Eq, RuntimeDebug, TypeInfo)]
    pub struct UserReputation {
        pub score: u32,
        pub positive_votes: u32,
        pub negative_votes: u32,
        pub last_updated: u64,
    }

    /// Storage for groups
    #[pallet::storage]
    #[pallet::getter(fn groups)]
    pub type Groups<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        u64, // Group ID
        GroupInfo<T::AccountId, <T::Currency as Currency<T::AccountId>>::Balance>,
        OptionQuery,
    >;

    /// Next available group ID
    #[pallet::storage]
    #[pallet::getter(fn next_group_id)]
    pub type NextGroupId<T> = StorageValue<_, u64, ValueQuery>;

    /// Group membership mapping
    #[pallet::storage]
    #[pallet::getter(fn group_members)]
    pub type GroupMembers<T: Config> = StorageDoubleMap<
        _,
        Blake2_128Concat,
        u64, // Group ID
        Blake2_128Concat,
        T::AccountId, // Member
        bool,
        ValueQuery,
    >;

    /// Group admin mapping
    #[pallet::storage]
    #[pallet::getter(fn group_admins)]
    pub type GroupAdmins<T: Config> = StorageDoubleMap<
        _,
        Blake2_128Concat,
        u64, // Group ID
        Blake2_128Concat,
        T::AccountId, // Admin
        bool,
        ValueQuery,
    >;

    /// Private messages storage
    #[pallet::storage]
    #[pallet::getter(fn private_messages)]
    pub type PrivateMessages<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        u64, // Message ID
        PrivateMessage<T::AccountId>,
        OptionQuery,
    >;

    /// Next available message ID
    #[pallet::storage]
    #[pallet::getter(fn next_message_id)]
    pub type NextMessageId<T> = StorageValue<_, u64, ValueQuery>;

    /// User's inbox (mapping from recipient to message IDs)
    #[pallet::storage]
    #[pallet::getter(fn user_inbox)]
    pub type UserInbox<T: Config> = StorageDoubleMap<
        _,
        Blake2_128Concat,
        T::AccountId, // Recipient
        Blake2_128Concat,
        u64, // Message ID
        bool,
        ValueQuery,
    >;

    /// Content reports storage
    #[pallet::storage]
    #[pallet::getter(fn content_reports)]
    pub type ContentReports<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        u64, // Report ID
        ContentReport<T::AccountId>,
        OptionQuery,
    >;

    /// Next available report ID
    #[pallet::storage]
    #[pallet::getter(fn next_report_id)]
    pub type NextReportId<T> = StorageValue<_, u64, ValueQuery>;

    /// User reputation storage
    #[pallet::storage]
    #[pallet::getter(fn user_reputation)]
    pub type UserReputations<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        T::AccountId,
        UserReputation,
        OptionQuery,
    >;

    /// Blocked users mapping
    #[pallet::storage]
    #[pallet::getter(fn blocked_users)]
    pub type BlockedUsers<T: Config> = StorageDoubleMap<
        _,
        Blake2_128Concat,
        T::AccountId, // Blocker
        Blake2_128Concat,
        T::AccountId, // Blocked
        bool,
        ValueQuery,
    >;

    /// Events emitted by this pallet
    #[pallet::event]
    #[pallet::generate_deposit(pub(super) fn deposit_event)]
    pub enum Event<T: Config> {
        /// A new group was created. [group_id, creator]
        GroupCreated { group_id: u64, creator: T::AccountId },
        /// User joined a group. [group_id, user]
        GroupJoined { group_id: u64, user: T::AccountId },
        /// User left a group. [group_id, user]
        GroupLeft { group_id: u64, user: T::AccountId },
        /// Group was updated. [group_id, updater]
        GroupUpdated { group_id: u64, updater: T::AccountId },
        /// Private message sent. [message_id, sender, recipient]
        PrivateMessageSent { message_id: u64, sender: T::AccountId, recipient: T::AccountId },
        /// Private message read. [message_id, reader]
        PrivateMessageRead { message_id: u64, reader: T::AccountId },
        /// Content reported. [report_id, reporter]
        ContentReported { report_id: u64, reporter: T::AccountId },
        /// Report status updated. [report_id, new_status]
        ReportStatusUpdated { report_id: u64, new_status: ReportStatus },
        /// User reputation updated. [user, new_score]
        ReputationUpdated { user: T::AccountId, new_score: u32 },
        /// User blocked another user. [blocker, blocked]
        UserBlocked { blocker: T::AccountId, blocked: T::AccountId },
        /// User unblocked another user. [unblocker, unblocked]
        UserUnblocked { unblocker: T::AccountId, unblocked: T::AccountId },
    }

    /// Errors that can occur when executing this pallet's extrinsics
    #[pallet::error]
    pub enum Error<T> {
        /// Group not found
        GroupNotFound,
        /// Group name too long
        GroupNameTooLong,
        /// Group description too long
        GroupDescriptionTooLong,
        /// Group is full
        GroupFull,
        /// Not a group member
        NotGroupMember,
        /// Not a group admin
        NotGroupAdmin,
        /// Already a group member
        AlreadyGroupMember,
        /// Message not found
        MessageNotFound,
        /// Message too long
        MessageTooLong,
        /// Cannot message yourself
        CannotMessageSelf,
        /// User is blocked
        UserBlocked,
        /// Report not found
        ReportNotFound,
        /// Cannot block yourself
        CannotBlockSelf,
        /// Already blocked
        AlreadyBlocked,
        /// Not blocked
        NotBlocked,
        /// Insufficient balance for deposit
        InsufficientBalance,
        /// Unauthorized operation
        Unauthorized,
    }

    #[pallet::call]
    impl<T: Config> Pallet<T> {
        /// Create a new group
        #[pallet::weight(10_000)]
        pub fn create_group(
            origin: OriginFor<T>,
            name: Vec<u8>,
            description: Vec<u8>,
            is_public: bool,
            avatar_hash: Option<Vec<u8>>,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;

            // Check name length
            ensure!(
                name.len() <= T::MaxGroupNameLength::get() as usize,
                Error::<T>::GroupNameTooLong
            );

            // Check description length
            ensure!(
                description.len() <= T::MaxGroupDescriptionLength::get() as usize,
                Error::<T>::GroupDescriptionTooLong
            );

            let deposit = T::GroupDeposit::get();
            
            // Reserve deposit
            T::Currency::reserve(&who, deposit)
                .map_err(|_| Error::<T>::InsufficientBalance)?;

            let group_id = Self::next_group_id();
            let timestamp = frame_system::Pallet::<T>::block_number().saturated_into::<u64>();

            let group_info = GroupInfo {
                creator: who.clone(),
                name,
                description,
                avatar_hash,
                member_count: 1,
                is_public,
                created_at: timestamp,
                deposit,
            };

            Groups::<T>::insert(&group_id, &group_info);
            NextGroupId::<T>::put(group_id + 1);

            // Add creator as member and admin
            GroupMembers::<T>::insert(&group_id, &who, true);
            GroupAdmins::<T>::insert(&group_id, &who, true);

            Self::deposit_event(Event::GroupCreated { group_id, creator: who });

            Ok(())
        }

        /// Join a group
        #[pallet::weight(10_000)]
        pub fn join_group(
            origin: OriginFor<T>,
            group_id: u64,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;

            let mut group = Self::groups(group_id).ok_or(Error::<T>::GroupNotFound)?;
            
            // Check if already a member
            ensure!(!Self::group_members(group_id, &who), Error::<T>::AlreadyGroupMember);
            
            // Check if group is full
            ensure!(
                group.member_count < T::MaxGroupMembers::get(),
                Error::<T>::GroupFull
            );

            // Add member
            GroupMembers::<T>::insert(&group_id, &who, true);
            group.member_count = group.member_count.saturating_add(1);
            Groups::<T>::insert(&group_id, &group);

            Self::deposit_event(Event::GroupJoined { group_id, user: who });

            Ok(())
        }

        /// Leave a group
        #[pallet::weight(10_000)]
        pub fn leave_group(
            origin: OriginFor<T>,
            group_id: u64,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;

            let mut group = Self::groups(group_id).ok_or(Error::<T>::GroupNotFound)?;
            
            // Check if member
            ensure!(Self::group_members(group_id, &who), Error::<T>::NotGroupMember);

            // Remove member
            GroupMembers::<T>::remove(&group_id, &who);
            GroupAdmins::<T>::remove(&group_id, &who);
            group.member_count = group.member_count.saturating_sub(1);
            Groups::<T>::insert(&group_id, &group);

            Self::deposit_event(Event::GroupLeft { group_id, user: who });

            Ok(())
        }

        /// Send a private message
        #[pallet::weight(10_000)]
        pub fn send_private_message(
            origin: OriginFor<T>,
            recipient: T::AccountId,
            content_hash: Vec<u8>,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;

            // Cannot message yourself
            ensure!(who != recipient, Error::<T>::CannotMessageSelf);

            // Check if sender is blocked by recipient
            ensure!(!Self::blocked_users(&recipient, &who), Error::<T>::UserBlocked);

            // Check message length
            ensure!(
                content_hash.len() <= T::MaxMessageLength::get() as usize,
                Error::<T>::MessageTooLong
            );

            let message_id = Self::next_message_id();
            let timestamp = frame_system::Pallet::<T>::block_number().saturated_into::<u64>();

            let message = PrivateMessage {
                sender: who.clone(),
                recipient: recipient.clone(),
                content_hash,
                timestamp,
                is_read: false,
            };

            PrivateMessages::<T>::insert(&message_id, &message);
            NextMessageId::<T>::put(message_id + 1);

            // Add to recipient's inbox
            UserInbox::<T>::insert(&recipient, &message_id, true);

            Self::deposit_event(Event::PrivateMessageSent { 
                message_id, 
                sender: who, 
                recipient 
            });

            Ok(())
        }

        /// Mark a private message as read
        #[pallet::weight(10_000)]
        pub fn mark_message_read(
            origin: OriginFor<T>,
            message_id: u64,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;

            let mut message = Self::private_messages(message_id).ok_or(Error::<T>::MessageNotFound)?;
            
            // Only recipient can mark as read
            ensure!(message.recipient == who, Error::<T>::Unauthorized);

            message.is_read = true;
            PrivateMessages::<T>::insert(&message_id, &message);

            Self::deposit_event(Event::PrivateMessageRead { message_id, reader: who });

            Ok(())
        }

        /// Report content or user
        #[pallet::weight(10_000)]
        pub fn report_content(
            origin: OriginFor<T>,
            target_account: Option<T::AccountId>,
            content_hash: Option<Vec<u8>>,
            reason: ReportReason,
            description: Vec<u8>,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;

            let report_id = Self::next_report_id();
            let timestamp = frame_system::Pallet::<T>::block_number().saturated_into::<u64>();

            let report = ContentReport {
                reporter: who.clone(),
                target_account,
                content_hash,
                reason,
                description,
                timestamp,
                status: ReportStatus::Pending,
            };

            ContentReports::<T>::insert(&report_id, &report);
            NextReportId::<T>::put(report_id + 1);

            Self::deposit_event(Event::ContentReported { report_id, reporter: who });

            Ok(())
        }

        /// Block a user
        #[pallet::weight(10_000)]
        pub fn block_user(
            origin: OriginFor<T>,
            target: T::AccountId,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;

            // Cannot block yourself
            ensure!(who != target, Error::<T>::CannotBlockSelf);
            
            // Check if already blocked
            ensure!(!Self::blocked_users(&who, &target), Error::<T>::AlreadyBlocked);

            BlockedUsers::<T>::insert(&who, &target, true);

            Self::deposit_event(Event::UserBlocked { blocker: who, blocked: target });

            Ok(())
        }

        /// Unblock a user
        #[pallet::weight(10_000)]
        pub fn unblock_user(
            origin: OriginFor<T>,
            target: T::AccountId,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;

            // Check if blocked
            ensure!(Self::blocked_users(&who, &target), Error::<T>::NotBlocked);

            BlockedUsers::<T>::remove(&who, &target);

            Self::deposit_event(Event::UserUnblocked { unblocker: who, unblocked: target });

            Ok(())
        }

        /// Update user reputation (admin only)
        #[pallet::weight(10_000)]
        pub fn update_reputation(
            origin: OriginFor<T>,
            target: T::AccountId,
            positive: bool,
        ) -> DispatchResult {
            let _who = ensure_signed(origin)?;
            // TODO: Add admin check

            let timestamp = frame_system::Pallet::<T>::block_number().saturated_into::<u64>();
            
            let mut reputation = Self::user_reputation(&target).unwrap_or(UserReputation {
                score: 100, // Default score
                positive_votes: 0,
                negative_votes: 0,
                last_updated: timestamp,
            });

            if positive {
                reputation.positive_votes = reputation.positive_votes.saturating_add(1);
                reputation.score = reputation.score.saturating_add(1);
            } else {
                reputation.negative_votes = reputation.negative_votes.saturating_add(1);
                reputation.score = reputation.score.saturating_sub(1);
            }

            reputation.last_updated = timestamp;
            UserReputations::<T>::insert(&target, &reputation);

            Self::deposit_event(Event::ReputationUpdated { 
                user: target, 
                new_score: reputation.score 
            });

            Ok(())
        }
    }
}

