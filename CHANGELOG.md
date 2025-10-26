# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added - 2024-01-02

#### User Management Enhancements

- **First Name and Last Name Fields**: Users now have `first_name` and `last_name` fields in addition to email
  - These fields are required when creating a new user
  - Both fields are stored in the database as non-nullable strings
  
- **Update User Endpoint**: New `PUT /users/{user_id}` endpoint to update existing users
  - Allows updating email, first_name, and last_name
  - All fields are optional in the update request
  - Email uniqueness validation ensures no duplicate emails
  - Returns updated user information
  
- **Database Migration**: New migration file `0002_add_user_names.py`
  - Adds `first_name` and `last_name` columns to the users table
  - Handles existing data by setting default values before making columns non-nullable
  - Includes rollback capability via downgrade function

#### API Changes

**POST /users/** - Create User
```json
{
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe"
}
```

**PUT /users/{user_id}** - Update User (New Endpoint)
```json
{
  "email": "newemail@example.com",
  "first_name": "Jane",
  "last_name": "Smith"
}
```

All fields in the update request are optional. Partial updates are supported.

#### Schema Changes

- `UserBase`: Now includes `first_name` and `last_name` fields
- `UserCreate`: Inherits `email`, `first_name`, and `last_name` from `UserBase`
- `UserUpdate`: New schema with all optional fields for partial updates
- `UserResponse`: Returns complete user information including names
- `UserWithWallets`: Enhanced to include first and last names with wallet information

#### Model Changes

- `User` model now includes:
  - `first_name` (String, required)
  - `last_name` (String, required)
  - All existing fields (id, email, created_at, updated_at)
  - Relationships to wallets maintained

### Technical Details

- Maintained backward compatibility through migration with default values
- Email uniqueness validation on both create and update operations
- Proper error handling with appropriate HTTP status codes (400, 404)
- Updated documentation in README.md with new endpoint information
- Improved code formatting for better readability

### Migration Instructions

To apply the new changes to an existing database:

```bash
alembic upgrade head
```

To rollback the changes:

```bash
alembic downgrade -1
```

### Breaking Changes

⚠️ **Important**: The `POST /users/` endpoint now requires `first_name` and `last_name` fields. 
Existing API clients must be updated to include these fields when creating new users.

### Files Modified

- `app/models/user.py` - Added first_name and last_name columns
- `app/schemas/user.py` - Updated schemas with name fields and UserUpdate
- `app/api/users.py` - Added update endpoint and modified create endpoint
- `alembic/versions/0002_add_user_names.py` - New migration file
- `README.md` - Updated documentation with new API information

## [1.0.0] - 2024-01-01

### Initial Release

- Real-time blockchain transaction monitoring
- WebSocket-based live status updates
- Multi-wallet support per user
- Blockchain reorganization detection
- Configurable confirmation requirements per network
- Docker containerization for easy deployment
- FastAPI REST API with user, wallet, and deposit management
- PostgreSQL database with SQLAlchemy ORM
- Alchemy API integration for Ethereum Sepolia testnet