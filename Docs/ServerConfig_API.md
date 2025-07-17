# Server Config API

The Server Config API provides access to some of the server settings. Regular or unauthenticated users have read-only access to a limited set of settings. You must authenticate as an administrator to have read-write access to all settings.

---

## Read Settings

Gets the server settings. Regular users or unauthenticated requests return only a subset of settings.

```bash
GET /server-config
```

**Example cURL Request (unauthenticated):**
```bash
curl https://canvus.example.com/api/v1/server-config
```

**Example Response (unauthenticated):**
```json
{
  "authentication": {
    "password": {
      "enabled": true,
      "sign_up_enabled": false
    },
    "qr_code": {
      "enabled": true
    },
    "saml": {
      "acs_url": "http://canvus.example.com/users/login/saml/callback",
      "enabled": true,
      "idp_cert_finger_print": "CA:F2:55:F8:F4:6D:E4:24:97:BE:3C:42:AC:CC:BA:41:51:D9:8F:EB:A3:1E:73:77:AB:5C:24:33:A3:5A:20:65",
      "idp_entity_id": "https://samltest.id/saml/idp",
      "idp_target_url": "https://samltest.id/idp/profile/SAML2/Redirect/SSO",
      "name_id_format": "urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress",
      "sign_up_enabled": true,
      "sp_entity_id": "canvus"
    }
  },
  "external_url": "http://canvus.example.com",
  "server_name": ""
}
```

**Example cURL Request (administrator):**
```bash
curl -H "Private-Token: <access token>" https://canvus.example.com/api/v1/server-config
```

**Example Response (administrator):**
```json
{
  "access": "rw",
  "authentication": {
    "domain_allow_list": [
      "example.com"
    ],
    "password": {
      "enabled": true,
      "sign_up_enabled": false
    },
    "qr_code": {
      "enabled": true
    },
    "require_admin_approval": true,
    "saml": {
      "acs_url": "http://canvus.example.com/users/login/saml/callback",
      "enabled": true,
      "idp_cert_finger_print": "CA:F2:55:F8:F4:6D:E4:24:97:BE:3C:42:AC:CC:BA:41:51:D9:8F:EB:A3:1E:73:77:AB:5C:24:33:A3:5A:20:65",
      "idp_entity_id": "https://samltest.id/saml/idp",
      "idp_target_url": "https://samltest.id/idp/profile/SAML2/Redirect/SSO",
      "name_id_format": "urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress",
      "sign_up_enabled": true,
      "sp_entity_id": "canvus"
    }
  },
  "email": {
    "mail_reply_to_address": "",
    "mail_reply_to_name": "",
    "mail_sender_address": "noreply@example.com",
    "mail_sender_name": "Noreply",
    "smtp_allow_self_signed_certificates": false,
    "smtp_host": "smtp.example.com",
    "smtp_password": "",
    "smtp_port": 25,
    "smtp_security": "none",
    "smtp_username": "noreply@example.com"
  },
  "external_url": "http://canvus.example.com",
  "server_name": ""
}
```

## Change Settings

Sets new values to server settings. You must authenticate as an administrator to access this endpoint.

```bash
PATCH /server-config
```

**Example cURL Request:**
```bash
curl -X PATCH -H "Private-Token: <access token>" -d '{"authentication":{"domain_allow_list":["example.com"],"password":{"sign_up_enabled":false}}}' https://canvus.example.com/api/v1/server-config
```

**Example Response:**
```json
{
  "access": "rw",
  "authentication": {
    "domain_allow_list": [
      "example.com"
    ],
    "password": {
      "enabled": true,
      "sign_up_enabled": false
    },
    "qr_code": {
      "enabled": true
    },
    "require_admin_approval": true,
    "saml": {
      "acs_url": "http://canvus.example.com/users/login/saml/callback",
      "enabled": true,
      "idp_cert_finger_print": "CA:F2:55:F8:F4:6D:E4:24:97:BE:3C:42:AC:CC:BA:41:51:D9:8F:EB:A3:1E:73:77:AB:5C:24:33:A3:5A:20:65",
      "idp_entity_id": "https://samltest.id/saml/idp",
      "idp_target_url": "https://samltest.id/idp/profile/SAML2/Redirect/SSO",
      "name_id_format": "urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress",
      "sign_up_enabled": true,
      "sp_entity_id": "canvus"
    }
  },
  "email": {
    "mail_reply_to_address": "",
    "mail_reply_to_name": "",
    "mail_sender_address": "noreply@example.com",
    "mail_sender_name": "Noreply",
    "smtp_allow_self_signed_certificates": false,
    "smtp_host": "smtp.example.com",
    "smtp_password": "",
    "smtp_port": 25,
    "smtp_security": "none",
    "smtp_username": "noreply@example.com"
  },
  "external_url": "http://canvus.example.com",
  "server_name": ""
}
```

## Send Test Email

Sends a test email to the email address of the user making the request. You must authenticate as an administrator to access this endpoint.

```bash
POST /server-config/send-test-email
```

**Example cURL Request:**
```bash
curl -X POST -H "Private-Token: <access token>" https://canvus.example.com/api/v1/server-config/send-test-email
``` 