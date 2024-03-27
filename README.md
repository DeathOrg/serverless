# serverless
Welcome to this wonderful repository dedicated to creating cloud functions in Google Cloud Platform (GCP). This repository contains several cloud functions designed to perform various tasks efficiently. Below is a brief overview of the cloud functions available in this repository:

## Cloud Functions

### 1. `send_verification_email`

This cloud function is responsible for sending verification emails to users who sign up for your service. It utilizes Mailgun for sending emails and generates unique verification codes for each user.

#### Functionality:
- Sends a verification email to the user's provided email address.
- Generates a unique verification code for each user.
- Tracks information about the sent verification email in the database.

#### Usage:
- Triggers: Pub/Sub message containing user data.
- Input: User data including first name, username, hostname, and verification API.
- Output: Sends a verification email to the provided email address.

## Cloud Function Details

### `generate_unique_verification_code(username)`

This function generates a unique verification code for a given username. It utilizes cryptographic methods to ensure the security of the generated code.

#### Parameters:
- `username`: The username of the user for whom to generate the code.

#### Returns:
- A unique verification code for the given username.

### `track_email(verification_link, username)`

This function tracks information about the sent verification email. It inserts the verification data into the database for further tracking.

#### Parameters:
- `verification_link`: The verification link sent to the user.
- `username`: The username of the user.

### `send_verification_email(event, context)`

This is the main cloud function responsible for sending verification emails to users. It decodes the Pub/Sub message, extracts necessary data, generates a verification code, constructs the email content, and sends the email using Mailgun.

#### Parameters:
- `event`: Pub/Sub message containing user data.
- `context`: Information about the event context.

## Setup Instructions

To deploy and use these cloud functions in your GCP environment, follow these steps:

1. Ensure you have set up a GCP project and have necessary permissions.
2. Set up Mailgun account and obtain API key and domain.
3. Set up a Cloud SQL instance and configure the necessary environment variables for database connection.
4. Deploy the cloud functions using the GCP Cloud Functions console or using the gcloud CLI.
5. Trigger the `send_verification_email` function with Pub/Sub messages containing user data.

Feel free to explore and customize these cloud functions according to your requirements. If you have any questions or need assistance, please don't hesitate to reach out.

Happy coding! 🚀
