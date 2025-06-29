#![cfg_attr(not(feature = "std"), no_std)]

/// AlphaCoin pallet for Alpha blockchain
/// 
/// This pallet implements the native AlphaCoin token functionality including:
/// - Token minting and burning
/// - Transfer operations
/// - Balance management
/// - Reward distribution for social activities

pub use pallet::*;

#[frame_support::pallet]
pub mod pallet {
    use frame_support::{
        dispatch::{DispatchResult, DispatchError},
        pallet_prelude::*,
        traits::{Get, Currency, ReservableCurrency},
        PalletId,
    };
    use frame_system::pallet_prelude::*;
    use sp_std::vec::Vec;
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

        /// The currency used for paying transaction fees and holding balances.
        type Currency: Currency<Self::AccountId> + ReservableCurrency<Self::AccountId>;

        /// The amount of currency needed to reserve for creating a social post.
        #[pallet::constant]
        type PostDeposit: Get<<Self::Currency as Currency<Self::AccountId>>::Balance>;

        /// Maximum length of a social post content.
        #[pallet::constant]
        type MaxPostLength: Get<u32>;

        /// Reward amount for creating a post.
        #[pallet::constant]
        type PostReward: Get<<Self::Currency as Currency<Self::AccountId>>::Balance>;

        /// Reward amount for receiving a like.
        #[pallet::constant]
        type LikeReward: Get<<Self::Currency as Currency<Self::AccountId>>::Balance>;

        /// The pallet's id, used for deriving its sovereign account ID.
        #[pallet::constant]
        type PalletId: Get<PalletId>;
    }

    /// Social post structure
    #[derive(Encode, Decode, Clone, PartialEq, Eq, RuntimeDebug, TypeInfo)]
    pub struct SocialPost<AccountId, Balance> {
        pub author: AccountId,
        pub content_hash: Vec<u8>, // IPFS hash of the content
        pub timestamp: u64,
        pub likes: u32,
        pub deposit: Balance,
    }

    /// Storage for social posts
    #[pallet::storage]
    #[pallet::getter(fn posts)]
    pub type Posts<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        u64, // Post ID
        SocialPost<T::AccountId, <T::Currency as Currency<T::AccountId>>::Balance>,
        OptionQuery,
    >;

    /// Next available post ID
    #[pallet::storage]
    #[pallet::getter(fn next_post_id)]
    pub type NextPostId<T> = StorageValue<_, u64, ValueQuery>;

    /// Mapping from post ID to accounts that liked it
    #[pallet::storage]
    #[pallet::getter(fn post_likes)]
    pub type PostLikes<T: Config> = StorageDoubleMap<
        _,
        Blake2_128Concat,
        u64, // Post ID
        Blake2_128Concat,
        T::AccountId, // Liker
        bool,
        ValueQuery,
    >;

    /// User profiles
    #[pallet::storage]
    #[pallet::getter(fn user_profiles)]
    pub type UserProfiles<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        T::AccountId,
        Vec<u8>, // IPFS hash of profile data
        OptionQuery,
    >;

    /// Following relationships
    #[pallet::storage]
    #[pallet::getter(fn following)]
    pub type Following<T: Config> = StorageDoubleMap<
        _,
        Blake2_128Concat,
        T::AccountId, // Follower
        Blake2_128Concat,
        T::AccountId, // Followed
        bool,
        ValueQuery,
    >;

    /// Events emitted by this pallet
    #[pallet::event]
    #[pallet::generate_deposit(pub(super) fn deposit_event)]
    pub enum Event<T: Config> {
        /// A new social post was created. [post_id, author]
        PostCreated { post_id: u64, author: T::AccountId },
        /// A post was liked. [post_id, liker, author]
        PostLiked { post_id: u64, liker: T::AccountId, author: T::AccountId },
        /// A post was unliked. [post_id, unliker, author]
        PostUnliked { post_id: u64, unliker: T::AccountId, author: T::AccountId },
        /// User profile was updated. [account]
        ProfileUpdated { account: T::AccountId },
        /// User followed another user. [follower, followed]
        UserFollowed { follower: T::AccountId, followed: T::AccountId },
        /// User unfollowed another user. [unfollower, unfollowed]
        UserUnfollowed { unfollower: T::AccountId, unfollowed: T::AccountId },
        /// Reward was distributed. [recipient, amount]
        RewardDistributed { recipient: T::AccountId, amount: <T::Currency as Currency<T::AccountId>>::Balance },
    }

    /// Errors that can occur when executing this pallet's extrinsics
    #[pallet::error]
    pub enum Error<T> {
        /// Post not found
        PostNotFound,
        /// Post content too long
        PostTooLong,
        /// Already liked this post
        AlreadyLiked,
        /// Haven't liked this post
        NotLiked,
        /// Cannot like own post
        CannotLikeOwnPost,
        /// Cannot follow yourself
        CannotFollowSelf,
        /// Already following this user
        AlreadyFollowing,
        /// Not following this user
        NotFollowing,
        /// Insufficient balance for deposit
        InsufficientBalance,
    }

    #[pallet::call]
    impl<T: Config> Pallet<T> {
        /// Create a new social post
        #[pallet::weight(10_000)]
        pub fn create_post(
            origin: OriginFor<T>,
            content_hash: Vec<u8>,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;

            // Check content length
            ensure!(
                content_hash.len() <= T::MaxPostLength::get() as usize,
                Error::<T>::PostTooLong
            );

            let deposit = T::PostDeposit::get();
            
            // Reserve deposit
            T::Currency::reserve(&who, deposit)
                .map_err(|_| Error::<T>::InsufficientBalance)?;

            let post_id = Self::next_post_id();
            let timestamp = frame_system::Pallet::<T>::block_number().saturated_into::<u64>();

            let post = SocialPost {
                author: who.clone(),
                content_hash,
                timestamp,
                likes: 0,
                deposit,
            };

            Posts::<T>::insert(&post_id, &post);
            NextPostId::<T>::put(post_id + 1);

            // Distribute reward for creating post
            let reward = T::PostReward::get();
            let _ = T::Currency::deposit_creating(&who, reward);

            Self::deposit_event(Event::PostCreated { post_id, author: who.clone() });
            Self::deposit_event(Event::RewardDistributed { recipient: who, amount: reward });

            Ok(())
        }

        /// Like a post
        #[pallet::weight(10_000)]
        pub fn like_post(
            origin: OriginFor<T>,
            post_id: u64,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;

            let mut post = Self::posts(post_id).ok_or(Error::<T>::PostNotFound)?;
            
            // Cannot like own post
            ensure!(post.author != who, Error::<T>::CannotLikeOwnPost);
            
            // Check if already liked
            ensure!(!Self::post_likes(post_id, &who), Error::<T>::AlreadyLiked);

            // Update like status
            PostLikes::<T>::insert(&post_id, &who, true);
            post.likes += 1;
            Posts::<T>::insert(&post_id, &post);

            // Distribute reward to post author
            let reward = T::LikeReward::get();
            let _ = T::Currency::deposit_creating(&post.author, reward);

            Self::deposit_event(Event::PostLiked { 
                post_id, 
                liker: who, 
                author: post.author.clone() 
            });
            Self::deposit_event(Event::RewardDistributed { 
                recipient: post.author, 
                amount: reward 
            });

            Ok(())
        }

        /// Unlike a post
        #[pallet::weight(10_000)]
        pub fn unlike_post(
            origin: OriginFor<T>,
            post_id: u64,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;

            let mut post = Self::posts(post_id).ok_or(Error::<T>::PostNotFound)?;
            
            // Check if liked
            ensure!(Self::post_likes(post_id, &who), Error::<T>::NotLiked);

            // Update like status
            PostLikes::<T>::remove(&post_id, &who);
            post.likes = post.likes.saturating_sub(1);
            Posts::<T>::insert(&post_id, &post);

            Self::deposit_event(Event::PostUnliked { 
                post_id, 
                unliker: who, 
                author: post.author 
            });

            Ok(())
        }

        /// Update user profile
        #[pallet::weight(10_000)]
        pub fn update_profile(
            origin: OriginFor<T>,
            profile_hash: Vec<u8>,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;

            UserProfiles::<T>::insert(&who, &profile_hash);

            Self::deposit_event(Event::ProfileUpdated { account: who });

            Ok(())
        }

        /// Follow a user
        #[pallet::weight(10_000)]
        pub fn follow_user(
            origin: OriginFor<T>,
            target: T::AccountId,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;

            // Cannot follow yourself
            ensure!(who != target, Error::<T>::CannotFollowSelf);
            
            // Check if already following
            ensure!(!Self::following(&who, &target), Error::<T>::AlreadyFollowing);

            Following::<T>::insert(&who, &target, true);

            Self::deposit_event(Event::UserFollowed { 
                follower: who, 
                followed: target 
            });

            Ok(())
        }

        /// Unfollow a user
        #[pallet::weight(10_000)]
        pub fn unfollow_user(
            origin: OriginFor<T>,
            target: T::AccountId,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;

            // Check if following
            ensure!(Self::following(&who, &target), Error::<T>::NotFollowing);

            Following::<T>::remove(&who, &target);

            Self::deposit_event(Event::UserUnfollowed { 
                unfollower: who, 
                unfollowed: target 
            });

            Ok(())
        }
    }
}

