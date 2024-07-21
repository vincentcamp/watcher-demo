# Sensecap Watcher Showcase Website

## Overview

This website serves as a comprehensive showcase for the new Sensecap Watcher, demonstrating its capabilities and data visualization features. The project integrates various technologies to create a seamless flow of data from the Watcher device to a user-friendly web interface.

## Technical Stack

- **Watcher API**: The core data source for the project.
- **Node-RED**: Used for data flow management and API integration.
- **MongoDB**: The database solution for storing and managing Watcher data.
- **Flask**: The web framework used to build the backend of the showcase website.
- **HTML/CSS/JavaScript**: Used for creating the frontend of the website.

## Development Process

### 1. API Integration

- Integrated the Watcher API into Node-RED, enabling real-time data flow from Watcher devices.
- Established a connection between Node-RED and MongoDB using the MongoDB API.
- This integration allows for efficient data collection and storage from Watcher devices.

### 2. Database Design

- Designed a MongoDB schema to effectively store and organize data from the Watcher devices.
- Implemented data standardization functions in the Flask backend to ensure consistency in data format across different Watcher models or versions.

### 3. Backend Development

- Developed a Flask application to serve as the backend for the showcase website.
- Implemented routes for fetching data from MongoDB and serving it to the frontend.
- Created API endpoints for receiving new data and updating the database in real-time.

### 4. Frontend Development

- Designed a responsive and visually appealing UI using HTML, CSS, and JavaScript.
- Implemented a grid layout to display Watcher data in an organized manner.
- Added interactive elements such as hover effects and animations to enhance user experience.
- Integrated a unique "firefly" cursor effect to add a dynamic and engaging visual element to the site.

### 5. Data Visualization

- Created individual detail pages for each Watcher device, displaying comprehensive information including images, timestamps, and other relevant data.
- Implemented a dropdown feature on detail pages to show additional information on demand.

### 6. Performance Optimization

- Utilized server-side rendering with Flask templates to improve initial page load times.
- Implemented lazy loading for images to enhance performance on slower connections.

### 7. Error Handling and Logging

- Implemented robust error handling and logging throughout the Flask application to facilitate debugging and maintenance.

### 8. Documentation

- Created a wiki page detailing the process of integrating the Watcher API with MongoDB through Node-RED (https://wiki.seeedstudio.com/watcher_node_red_to_mongodb).
- This documentation serves as a valuable resource for other developers looking to implement similar systems.
