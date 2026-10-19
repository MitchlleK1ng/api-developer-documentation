# API Error Handling Guide

## 1. Overview

The ContentMG API uses HTTP status codes to communicate the outcome of client requests.

When a request fails, the response should help developers understand the nature of the problem and determine the appropriate corrective action.

This guide describes the proposed error-handling conventions for the ContentMG API.

**Implementation status:** The status codes and response structures in this guide are proposed specifications. They must be verified against the working API before publication as confirmed behavior.

## 2. HTTP Status Codes

The following table identifies the HTTP status codes proposed for common API outcomes.

| Status code                 | Meaning                                                            | Recommended action                                                             |
| --------------------------- | ------------------------------------------------------------------ | ------------------------------------------------------------------------------ |
| `200 OK`                    | The request succeeded.                                             | Process the returned response.                                                 |
| `201 Created`               | A resource was created successfully.                               | Record the returned resource identifier if applicable.                         |
| `204 No Content`            | The request succeeded without a response body.                     | Treat the operation as successful without attempting to parse a response body. |
| `400 Bad Request`           | The request is malformed or otherwise invalid.                     | Review the request syntax and parameters.                                      |
| `401 Unauthorized`          | Valid authentication credentials are missing or were not accepted. | Check the authentication header and token.                                     |
| `403 Forbidden`             | The caller does not have permission to perform the operation.      | Verify the caller's permissions.                                               |
| `404 Not Found`             | The requested resource or route does not exist.                    | Check the endpoint path and resource identifier.                               |
| `409 Conflict`              | The request conflicts with the current resource state.             | Review the resource state and resolve the conflict.                            |
| `422 Unprocessable Content` | The request content fails a defined validation rule.               | Correct the invalid fields and resubmit the request.                           |
| `429 Too Many Requests`     | The client has exceeded an applicable rate limit.                  | Follow the documented rate-limit guidance before retrying.                     |
| `500 Internal Server Error` | The server encountered an unexpected condition.                    | Retry only when appropriate and report persistent failures.                    |
| `503 Service Unavailable`   | The service cannot currently handle the request.                   | Follow any retry guidance or `Retry-After` header supplied by the server.      |

The implementation may use only a subset of these status codes. The published reference must reflect the actual behavior of each endpoint.

## 3. Error Response Format

ContentMG should provide a consistent, machine-readable error response for applicable failures.

The following JSON illustrates a proposed error structure:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The request contains invalid fields.",
    "details": [
      {
        "field": "email",
        "issue": "The email address is invalid."
      }
    ]
  }
}
```

The fields in this example are proposed. Their names, data types, and availability must be confirmed against the implementation.

Error messages should explain the problem without exposing access tokens, passwords, internal credentials, or sensitive server information.

## 4. Common Error Scenarios

### 4.1 Invalid Request

**Possible status:** `400 Bad Request`

An invalid request may contain malformed JSON, incorrectly formatted parameters, or missing values required by the endpoint.

**Recommended action:**

1. Review the endpoint documentation.
2. Confirm that the request uses the correct HTTP method.
3. Validate the JSON syntax.
4. Check the required fields and parameter formats.
5. Submit the corrected request.

The actual validation rules must be documented for each endpoint.

### 4.2 Authentication Failure

**Possible status:** `401 Unauthorized`

An authentication failure occurs when the API cannot accept the credentials supplied with a request.

**Recommended action:**

1. Confirm that the Authorization header is present.
2. Verify the Bearer token format.
3. Check whether the token is valid and has expired.
4. Obtain valid credentials through the configured authentication process.

Never include real access tokens in support requests or publicly shared logs.

### 4.3 Insufficient Permissions

**Possible status:** `403 Forbidden`

A caller may be authenticated but lack permission to access a resource or perform an operation.

**Recommended action:**

1. Confirm the identity associated with the request.
2. Review the permissions assigned to that identity.
3. Request the appropriate access through the authorized administrator if necessary.

### 4.4 Resource Not Found

**Possible status:** `404 Not Found`

The requested resource may not exist, or the endpoint path or identifier may be incorrect.

**Recommended action:**

1. Check the resource identifier.
2. Confirm that the resource exists.
3. Verify the endpoint path and API version.
4. Confirm that the caller is using the correct environment.

The implementation must define how it distinguishes missing resources from nonexistent routes.

### 4.5 Rate Limit Exceeded

**Possible status:** `429 Too Many Requests`

The client has exceeded an applicable request limit.

**Recommended action:**

1. Review any rate-limit headers returned by the API.
2. Follow the server's retry instructions.
3. Use exponential backoff where appropriate.
4. Avoid repeatedly retrying requests without a delay.

The actual rate limits and response headers must be documented once established.

### 4.6 Server Error

**Possible status:** `500 Internal Server Error`

An unexpected server-side failure prevented the request from completing normally.

**Recommended action:**

1. Check whether the failure is temporary.
2. Review the response for a documented error identifier.
3. Retry only when appropriate for the operation.
4. Report persistent failures with the request time and relevant non-sensitive diagnostic information.

Do not expose internal stack traces or sensitive implementation details in public error responses.

## 5. Retry Guidance

Not every failed request should be retried automatically.

Before retrying, consider the status code, the operation's behavior, and whether the request may already have changed server state.

For example, a timed-out resource-creation request may have succeeded on the server even though the client did not receive the response.

The implementation should define an appropriate strategy for retrying requests that could create duplicate records or repeat other side effects.

Where supported, clients should follow documented retry headers and use backoff to avoid overwhelming the service.

## 6. Troubleshooting Checklist

When an API request fails, check the following:

* Is the base URL correct?
* Is the endpoint path correct?
* Does the HTTP method match the documented operation?
* Are required request headers present?
* Is authentication configured correctly?
* Does the request body match the documented schema?
* Are required fields present and valid?
* Does the response contain an error code or diagnostic message?
* Are rate limits or temporary service problems affecting the request?

## 7. Validation Requirements

Before this guide is published as verified API documentation, confirm that:

* The API returns the documented status codes for applicable conditions.
* Error response bodies match the documented schema.
* Authentication failures are handled consistently.
* Missing resources produce the expected responses.
* Invalid input is rejected according to the defined validation rules.
* Rate-limit behavior matches the documented guidance, if rate limiting is implemented.
* Error responses do not expose sensitive information.
* Retry guidance is appropriate for the affected operation.

Record actual test results and update this guide to match the implementation.

## 8. Documentation Maintenance

Review this guide whenever the API's error codes, response schemas, validation rules, authentication behavior, or retry policies change.

Coordinate reviews with the relevant technical stakeholders before publishing significant changes.

Record important documentation updates in the project changelog.
