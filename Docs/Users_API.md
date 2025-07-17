# Users API

The Users API provides access to user accounts on the server.

> **Note:**
> - Regular users can list other users, change their own profile data (such as name, password, etc.), or block themselves.
> - Administrators can modify other users, create new user accounts, and execute admin-only tasks such as approving new users.
> - **Group membership for users is managed through the [Groups API](./Groups_API.md).**

---

## List Users

Gets a list of all users.

```bash
GET /users
```

| Attribute           | Type    | Required | Description   |
|---------------------|---------|----------|---------------|
| `subscribe` (query) | boolean | no       | See Streaming |

**Example cURL Request:**
```bash
curl -H "Private-Token: <access token>" https://canvus.example.com/api/v1/users
```

**Example Response:**
```json
[
  {
    "admin": false,
    "approved": true,
    "blocked": false,
    "created_at": "2021-07-02T06:36:18.817Z",
    "email": "",
    "id": 100,
    "last_login": "2021-07-02T06:37:48.569Z",
    "name": "Guest",
    "state": "normal"
  },
  {
    "admin": true,
    "approved": true,
    "blocked": false,
    "created_at": "2021-07-02T06:36:33.392Z",
    "email": "admin@example.com",
    "id": 1000,
    "last_login": "2021-07-02T06:38:36.549Z",
    "name": "admin",
    "state": "normal"
  },
  {
    "admin": false,
    "approved": true,
    "blocked": false,
    "created_at": "2021-07-02T06:38:37.141Z",
    "email": "alice@example.com",
    "id": 1002,
    "last_login": "",
    "name": "Alice",
    "state": "normal"
  }
]
```

---

## Single User

Gets info about a single user.

```bash
GET /users/:id
```

| Attribute           | Type    | Required | Description                  |
|---------------------|---------|----------|------------------------------|
| `id` (path)         | integer | yes      | The ID of the user to get    |
| `subscribe` (query) | boolean | no       | See Streaming                |

**Example cURL Request:**
```bash
curl -H "Private-Token: <access token>" https://canvus.example.com/api/v1/users/1002
```

**Example Response:**
```json
{
  "admin": false,
  "approved": true,
  "blocked": false,
  "created_at": "2021-07-02T06:38:37.141Z",
  "email": "alice@example.com",
  "id": 1002,
  "last_login": "",
  "name": "Alice",
  "state": "normal"
}
```

---

## Create User

Creates a new user. You must authenticate as an administrator to use this endpoint.

> **Tip:** Unauthenticated requests can be made to the [Register User](#register-user) endpoint.

```bash
POST /users
```

| Attribute   | Type    | Required | Description                                                                 |
|-------------|---------|----------|-----------------------------------------------------------------------------|
| `email`     | string  | yes      | Email (used also as the login name) of the user. Must be unique.            |
| `name`      | string  | yes      | Display name of the user                                                    |
| `password`  | string  | no       | Password of the user. If missing, server sends password reset email         |
| `admin`     | boolean | no       | If true, the new user is admin. Default is false.                           |
| `approved`  | boolean | no       | If true, the new user is initially approved. Default depends on server      |
| `blocked`   | boolean | no       | If true, the new user is initially blocked. Default is false.               |

**Example cURL Request:**
```bash
curl -X POST -H "Private-Token: <access token>" -d '{"email":"bob@example.com","password":"BBBB","name":"Bob"}' https://canvus.example.com/api/v1/users
```

**Example Response:**
```json
{
  "admin": false,
  "approved": true,
  "blocked": false,
  "created_at": "2021-07-02T06:38:37.501Z",
  "email": "bob@example.com",
  "id": 1003,
  "last_login": "",
  "name": "Bob",
  "state": "normal"
}
```

---

## Delete User

Permanently deletes a user. You must authenticate as an administrator to use this endpoint.

```bash
DELETE /users/:id
```

| Attribute   | Type    | Required | Description                  |
|-------------|---------|----------|------------------------------|
| `id` (path) | integer | yes      | The ID of the user to delete |

**Example cURL Request:**
```bash
curl -X DELETE -H "Private-Token: <access token>" https://canvus.example.com/api/v1/users/1003
```

---

## Register User

Registers a new user account. This endpoint does not require authentication.

> **Tip:** Registering new users can be disabled in the server settings.

On success, this endpoint will send an email with a confirmation token to the provided email address. The new user account is not active until the email address is confirmed.

```bash
POST /users/register
```

| Attribute   | Type    | Required | Description                                                                 |
|-------------|---------|----------|-----------------------------------------------------------------------------|
| `email`     | string  | yes      | Email (used also as the login name) of the user. Must be unique.            |
| `name`      | string  | yes      | Display name of the user                                                    |
| `password`  | string  | yes      | Password of the user                                                        |
| `admin`     | boolean | no       | If true, the new user is admin. Default is false. Only admin can set true.  |
| `approved`  | boolean | no       | If user needs approval. Default depends on server. Only admin can set true. |
| `blocked`   | boolean | no       | If true, the new user is initially blocked. Default is false.               |

**Example cURL Request:**
```bash
curl -X POST -d '{"email":"carol@example.com","password":"CCCC","name":"Carol"}' https://canvus.example.com/api/v1/users/register
```

**Example Response:**
```json
{
  "msg": "Sign-up using a password is not enabled"
}
```

---

## Approve User

Approves registered user accounts pending approval. You must authenticate as an administrator to use this endpoint.

```bash
POST /users/:id/approve
```

| Attribute   | Type    | Required | Description                  |
|-------------|---------|----------|------------------------------|
| `id` (path) | integer | yes      | ID of the user               |

**Example cURL Request:**
```bash
curl -X POST -H "Private-Token: <access token>" https://canvus.example.com/api/v1/users/1002/approve
```

**Example Response:**
```json
{
  "admin": false,
  "approved": true,
  "blocked": false,
  "created_at": "2021-07-02T06:38:37.141Z",
  "email": "alice@example.com",
  "id": 1002,
  "last_login": "",
  "name": "Alice",
  "state": "normal"
}
```

---

## Email Confirmation

Confirms user email address with the token from email. This endpoint does not require authentication.

```bash
POST /users/confirm-email
```

| Attribute | Type   | Required | Description         |
|-----------|--------|----------|---------------------|
| `token`   | string | yes      | Token from the email|

**Example cURL Request:**
```bash
curl -X POST -d '{"token":"AAAAAAAAAAAAAAA"}' https://canvus.example.com/api/v1/users/confirm-email
```

**Example Response:**
```json
{
  "msg": "Invalid email confirmation token."
}
```

---

## Change Password

Allows a user to change their own password by providing the current and new password. Administrators can use this endpoint to change passwords of other regular users.

```bash
POST /users/:id/password
```

| Attribute           | Type    | Required | Description         |
|---------------------|---------|----------|---------------------|
| `id` (path)         | integer | yes      | ID of the user      |
| `current_password`  | string  | yes      | Old password        |
| `new_password`      | string  | yes      | New password        |

**Example cURL Request:**
```bash
curl -X POST -H "Private-Token: <access token>" -d '{"current_password":"AAAA","new_password":"BBBB"}' https://canvus.example.com/api/v1/users/1002/password
```

**Example Response:**
```json
{
  "admin": false,
  "approved": true,
  "blocked": false,
  "created_at": "2021-07-02T06:38:37.141Z",
  "email": "alice@example.com",
  "id": 1002,
  "last_login": "",
  "name": "Alice",
  "state": "normal"
}
```

---

## Request Password Reset

Sends an email with a password reset token to the email address of the user making the request. This endpoint does not require authentication.

```bash
POST /users/password/create-reset-token
```

| Attribute | Type   | Required | Description         |
|-----------|--------|----------|---------------------|
| `email`   | string | yes      | Email of the user   |

**Example cURL Request:**
```bash
curl -X POST -d '{"email":"bob@example.com"}' https://canvus.example.com/api/v1/users/password/create-reset-token
```

---

## Validate Password Reset Token

Validates a password reset token, but does not consume it. This endpoint is available without authentication.

```bash
GET /users/password/validate-reset-token
```

| Attribute      | Type   | Required | Description         |
|----------------|--------|----------|---------------------|
| `token` (query)| string | yes      | Token from the email|

**Example cURL Request:**
```bash
curl https://canvus.example.com/api/v1/users/password/validate-reset-token?token=AAAAAAAAAAAAAAA
```

**Example Response:**
```json
{
  "msg": "Invalid token"
}
```

---

## Reset Password

Resets a user password using the provided token from password reset email. This endpoint is available without authentication.

```bash
POST /users/password/reset
```

| Attribute | Type   | Required | Description         |
|-----------|--------|----------|---------------------|
| `token`   | string | yes      | Token from the email|
| `password`| string | yes      | New password        |

**Example cURL Request:**
```bash
curl -X POST -d '{"token":"AAAAAAAAAAAAAAA","password":"DDDD"}' https://canvus.example.com/api/v1/users/password/reset
```

**Example Response:**
```json
{
  "msg": "Invalid token"
}
```

---

## Sign In User

Signs the user in and issues an access token. This endpoint is available without authentication.

```bash
POST /users/login
```

| Attribute | Type   | Required | Description         |
|-----------|--------|----------|---------------------|
| `email`   | string | yes      | User email          |
| `password`| string | yes      | User password       |

**Example cURL Request:**
```bash
curl -X POST -d '{"email":"alice@example.com","password":"BBBB"}' https://canvus.example.com/api/v1/users/login
```

**Example Response:**
```json
{
  "token": "lmFU9obmM5v4o6jdCXsRW6v5bLD9w47aGIP4eMRnf3A",
  "user": {
    "admin": false,
    "approved": true,
    "blocked": false,
    "created_at": "2021-07-02T06:38:37.141Z",
    "email": "alice@example.com",
    "id": 1002,
    "last_login": "",
    "name": "Alice",
    "state": "normal"
  }
}
```

Alternatively, this endpoint can validate an existing token. If the token is valid, the token lifetime is prolonged.

| Attribute | Type   | Required | Description         |
|-----------|--------|----------|---------------------|
| `token`   | string | yes      | Access token        |

**Example cURL Request:**
```bash
curl -X POST -d '{"token":"z_Ttm-tcFpiadMUR2A_8kQnkOsl6wmcEKplotULC9fk"}' https://canvus.example.com/api/v1/users/login
```

**Example Response:**
```json
{
  "token": "n8_ZgoRHKnQWJnxdgT7s12jfWH5VGuNzpnps3PGZzwo",
  "user": {
    "admin": false,
    "approved": true,
    "blocked": false,
    "created_at": "2021-07-02T06:38:37.141Z",
    "email": "alice@example.com",
    "id": 1002,
    "last_login": "2021-07-02T06:38:38.722Z",
    "name": "Alice",
    "state": "normal"
  }
}
```

---

## Sign Out User

Signs the user out by invalidating the provided access token.

```bash
POST /users/logout
```

| Attribute | Type   | Required | Description         |
|-----------|--------|----------|---------------------|
| `token`   | string | no       | Token to invalidate. If empty, the Private-Token is used. |

**Example cURL Request:**
```bash
curl -X POST -H "Private-Token: <access token>" -d '{"token":"z_Ttm-tcFpiadMUR2A_8kQnkOsl6wmcEKplotULC9fk"}' https://canvus.example.com/api/v1/users/logout
```

---

## Block a User

Blocks a user. Blocked users cannot sign in. Regular users can only block their own account. Administrators can block any user.

```bash
POST /users/:id/block
```

| Attribute   | Type    | Required | Description         |
|-------------|---------|----------|---------------------|
| `id` (path) | integer | yes      | ID of the user      |

**Example cURL Request:**
```bash
curl -X POST -H "Private-Token: <access token>" https://canvus.example.com/api/v1/users/1002/block
```

**Example Response:**
```json
{
  "admin": false,
  "approved": true,
  "blocked": true,
  "created_at": "2021-07-02T06:38:37.141Z",
  "email": "alice@example.com",
  "id": 1002,
  "last_login": "2021-07-02T06:38:38.744Z",
  "name": "Alice",
  "state": "normal"
}
```

---

## Unblock a User

Unblocks a user. You must authenticate as an administrator to use this endpoint.

```bash
POST /users/:id/unblock
```

| Attribute   | Type    | Required | Description         |
|-------------|---------|----------|---------------------|
| `id` (path) | integer | yes      | ID of the user      |

**Example cURL Request:**
```bash
curl -X POST -H "Private-Token: <access token>" https://canvus.example.com/api/v1/users/1002/unblock
```

**Example Response:**
```json
{
  "admin": false,
  "approved": true,
  "blocked": false,
  "created_at": "2021-07-02T06:38:37.141Z",
  "email": "alice@example.com",
  "id": 1002,
  "last_login": "2021-07-02T06:38:38.744Z",
  "name": "Alice",
  "state": "normal"
}
```

---

## Set User Info

Changes user profile data such as name or email. Regular users can change only their own profile and only certain fields; administrators can change all fields of any user.

```bash
PATCH /users/:id
```

| Attribute                | Type    | Required | Description                                                                 |
|--------------------------|---------|----------|-----------------------------------------------------------------------------|
| `id` (path)              | integer | yes      | ID of the user                                                              |
| `email`                  | string  | no       | Email (used also as the login name) of the user. Must be unique.            |
| `name`                   | string  | no       | Display name of the user                                                    |
| `password`               | string  | no       | Password of the user. Admin-only.                                           |
| `admin`                  | boolean | no       | If true, the user is admin. Admin-only.                                     |
| `approved`               | boolean | no       | If true, the user is approved. Only from false to true. Admin-only.         |
| `blocked`                | boolean | no       | If true, the user is blocked.                                               |
| `need_email_confirmation`| boolean | no       | If true, user has confirmed email. Only from false to true. Admin-only.     |

**Example cURL Request:**
```bash
curl -X PATCH -H "Private-Token: <access token>" -d '{"name":"Alice Cooper"}' https://canvus.example.com/api/v1/users/1002
```

**Example Response:**
```json
{
  "admin": false,
  "approved": true,
  "blocked": false,
  "created_at": "2021-07-02T06:38:37.141Z",
  "email": "alice@example.com",
  "id": 1002,
  "last_login": "2021-07-02T06:38:38.744Z",
  "name": "Alice Cooper",
  "state": "normal"
}
```

---

## SAML 2.0 Sign-in

Implements SAML 2.0 ACS endpoint. Validates a SAML assertion and on success signs in the user and issues access token. SAML sign-in can be disabled in server settings. This endpoint is available without authentication.

```bash
POST /users/login/saml
```

| Attribute      | Type   | Required | Description                         |
|--------------- |--------|----------|-------------------------------------|
| `inResponseTo` | string | yes      | Cookie known to the initiator       |
| `responseXml`  | string | yes      | SAML assertion XML                  | 