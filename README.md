

# TrackMyWebsite

TrackMyWebsite is a robust Django-based web application designed to simplify URL management, enhance user tracking, and empower data-driven decision-making. With a comprehensive set of features, it allows users to create short URLs, monitor user locations, and analyze click data for a wide range of applications, from marketing campaigns to data collection projects.

## Table of Contents

- [TrackMyWebsite](#trackmywebsite)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
    - [User Authentication](#user-authentication)
    - [Short URL Management](#short-url-management)
    - [Edit and List Short URLs](#edit-and-list-short-urls)
    - [URL Redirection](#url-redirection)
    - [Deactivate URLs](#deactivate-urls)
    - [QR Code Generation](#qr-code-generation)
    - [User Location Tracking](#user-location-tracking)
    - [Visualize Location Data](#visualize-location-data)
    - [Export Location Information](#export-location-information)
    - [Click Data Analysis](#click-data-analysis)
  - [Prerequisites](#prerequisites)
  - [Environment Variables](#environment-variables)
  - [Installation](#installation)
  - [License](#license)
  - [Acknowledgments](#acknowledgments)
  - [Contributing](#contributing)
  - [Authors](#authors)
  - [Contact](#contact)

## Features

### User Authentication

- **Description**: Secure user authentication is implemented using Django's built-in mechanisms, ensuring a protected environment for URL management.
- **Usage**: Users can register and log in to their accounts, providing a personalized experience.

### Short URL Management

- **Description**: Users can create short URLs with ease, simplifying link sharing and tracking.
- **Features**:
    - Validation ensures the URL is valid and unique.
    - Custom short codes can be generated.
    - Expiry dates and custom notes can be added to URLs.
    - Password protection enhances security.
    - Accurate location tracking enables location-based access.
    - Short URLs are associated with the logged-in user, facilitating user-specific tracking.

### Edit and List Short URLs

- **Description**: Users can edit existing short URLs and efficiently manage their link portfolio.
- **Usage**: Form data is validated before saving changes, guaranteeing data integrity.

### URL Redirection

- **Description**: Access short URLs, which seamlessly redirect to the original links.
- **Features**:
    - Expiry date checks ensure link relevance.
    - Password protection provides an extra layer of security.

### Deactivate URLs

- **Description**: Users can deactivate short URLs to restrict further access.
- **Usage**: A user-friendly confirmation page streamlines the deactivation process.

### QR Code Generation

- **Description**: Generate QR codes for short URLs to simplify link sharing and scanning.
- **Usage**: QR codes are created using the `qrcode` library and served as image responses.

### User Location Tracking

- **Description**: Track user locations when they access short URLs, collecting valuable data for analysis.
- **Features**:
    - Gathered information includes IP addresses and geographic data.
    - Data is stored in the `UserLocation` model for future analysis.

### Visualize Location Data

- **Description**: Users can view a list of user locations associated with short URLs, promoting transparency.
- **Features**:
    - Display locations on a map using the Folium library, enhancing visualization.
    - Pagination ensures a manageable presentation of location data.

### Export Location Information

- **Description**: Copy location information as a text file for each entry, enabling data sharing and further analysis.

### Click Data Analysis

- **Description**: Analyze click data for short URLs, gaining invaluable insights into link performance.
- **Features**:
    - Data includes daily, monthly, yearly, and total click counts.
    - User countries, browsers, and platforms are tracked and presented.
    - Visualizations assist in data-driven decision-making.

## Prerequisites

Before using TrackMyWebsite, ensure you have the following prerequisites:

- Python 3.8 or later
- Django 3.9 or later

## Environment Variables

To run this project, set the following environment variables in your `.env` file:

- `BOT_TOKEN`: Telegram bot token for sending data to a Telegram chat.
- `CHAT_ID`: Chat ID for the Telegram chat where data is sent.
- `SERVER_ADDRESS`: Address for the server.
- `SECRET_KEY`: Secret key for Django's security mechanisms.
- `EMAIL_HOST_USER`: Email host username for sending verification emails.
- `EMAIL_HOST_PASSWORD`: Email host password for sending verification emails.

## Installation

1. Clone the repository:
    
    ```bash
    git clone https://github.com/Paresh-Maheshwari/TrackMyWebsite.git
    cd TrackMyWebsite
    ```
    
2. Create a virtual environment:
    
    ```bash
    python -m venv venv
    
    ```
    
3. Activate the virtual environment:
    - On Windows:
        
        ```bash
        venv\\Scripts\\activate
        
        ```
        
    - On macOS and Linux:
        
        ```bash
        source venv/bin/activate
        
        ```
        
4. Install dependencies:
    
    ```bash
    pip install -r requirements.txt
    
    ```
    
5. Run the project:
    
    ```bash
    python manage.py runserver
    
    ```
    
6. Access the project in your web browser at `http://localhost:8000/`.


## License

This project is licensed under the [MIT](https://choosealicense.com/licenses/mit/) License 

## Acknowledgments

- [Django](https://www.djangoproject.com/) - The web framework used for this project.
- [qrcode](https://pypi.org/project/qrcode/) - Library for generating QR codes.
- [Folium](https://python-visualization.github.io/folium/) - Library for creating interactive maps.

## Contributing

Contributions are welcome and greatly appreciated. To contribute to the project, please follow these steps:

- Fork the repository.
- Create a new branch for your feature or bug fix.
- Commit your changes and push to the new branch.
- Create a pull request.

## Authors

- [Paresh Maheshwari](https://github.com/Paresh-Maheshwari)

## Contact

If you have any questions or feedback, feel free to reach out to [pareshsurya721@gmail.com](mailto:your.email@example.com).
