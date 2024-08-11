# Dining Concierge Bot

This repository contains the code for a Dining Concierge Bot, designed to provide restaurant recommendations based on user preferences using the Yelp API and AWS Lambda functions.

## Project Overview

The **Dining Concierge Bot** streamlines the process of finding restaurants that meet specific user preferences. Leveraging the Yelp API, it accesses a vast database of dining options and integrates AWS Lambda for efficient backend processing, ensuring users receive timely and relevant recommendations.

## Features in Detail

### 1. Restaurant Recommendations
- **User Interaction:** Users input their dining preferences, such as cuisine type, location, and price range.
- **Yelp API Query:** The bot processes the input and queries the Yelp API to find restaurants matching the criteria.
- **Results Display:** A curated list of dining options is displayed to the user.

### 2. AWS Lambda Integration
- **Serverless Execution:** The bot’s backend is powered by AWS Lambda, handling user inputs, making API requests, and filtering results.
- **Scalability:** AWS Lambda allows for scalable and serverless execution, reducing the need for dedicated servers and ensuring the service can handle varying levels of demand.

### 3. Yelp API Integration
- **Restaurant Data:** The bot retrieves data from the Yelp Fusion API, including ratings, reviews, and locations.
- **Accurate Information:** Users receive up-to-date information about dining options, ensuring they have access to the latest details.

### 4. Frontend Interface
- **User-Friendly Design:** The frontend provides an intuitive interface for users to interact with the bot, making it easy to input preferences and receive recommendations.
- **Seamless Experience:** The design focuses on delivering a seamless experience, with straightforward input methods and clear results display.

## How It Works

1. **User Input:** Users enter their dining preferences via the frontend.
2. **Lambda Processing:** The AWS Lambda function processes the request, interacts with the Yelp API, and generates a list of recommended restaurants.
3. **Recommendation Display:** The frontend displays the recommendations, allowing users to explore their options.

## Benefits of the Project

- **Scalability:** AWS Lambda’s serverless architecture makes the bot highly scalable, capable of handling large volumes of requests.
- **Efficiency:** Automates the process of finding suitable restaurants, saving users time and effort.
- **Up-to-Date Information:** Provides the most current information through Yelp API integration, ensuring accurate and relevant recommendations.

## Installation

1. **Clone the repository:**
    ```bash
    git clone https://github.com/g-an24/Dining_Concierge_Bot.git
    cd Dining_Concierge_Bot
    ```

2. **Install dependencies:**
    - Navigate to the `Frontend` and `Lambda` directories and install the necessary packages:
    ```bash
    cd Frontend
    npm install
    cd ../Lambda
    pip install -r requirements.txt
    ```

3. **Setup AWS Lambda:**
    - Deploy the Lambda function using the AWS CLI or through the AWS Management Console.

## Usage

1. **Running the Frontend:**
    ```bash
    cd Frontend
    npm start
    ```
2. **Interacting with the Bot:**
   - Use the provided frontend interface to input dining preferences.
   - The bot will fetch and display restaurant recommendations.

## Project Structure

- **API/** - Contains scripts for interacting with the Yelp API.
- **Frontend/** - Contains the frontend code for user interaction.
- **Lambda/** - Contains AWS Lambda functions for backend processing.
- **yelp/** - Configuration and utility scripts for Yelp API interaction.

## Contributing

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes.
4. Commit your changes (`git commit -m 'Add some feature'`).
5. Push to the branch (`git push origin feature-branch`).
6. Create a Pull Request.

## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.
