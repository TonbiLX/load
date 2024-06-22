# Container Loading Visualization

This project aims to provide a visualization tool for loading containers with different products. It helps in calculating the total weight, volume, and remaining capacity of a container based on the dimensions and quantities of various products. The project uses Python for data processing and visualization.

## Features

- **Data Input and Processing:**
  - Input product details including name, dimensions (length, width, height), weight, and quantity.
  - Calculate the volume and total weight for each product.
  - Summarize the total volume and weight of all products.

- **Capacity Calculation:**
  - Calculate the remaining volume and weight capacity of the container.
  - Display the status of loading completion.

- **Visualization:**
  - 3D visualization of the container and the arrangement of products inside it.
  - Visual representation of product dimensions and positions within the container.
  - Display the container's fill percentage.

## Dependencies

- **pandas:** For data manipulation and calculation.
- **matplotlib:** For 3D visualization of the container and products.

## Installation

The project uses Poetry for dependency management. Ensure Poetry is installed on your system, then follow these steps to set up the project:

1. **Install Dependencies:**

    ```sh
    poetry install
    ```

2. **Run the Program:**

    ```sh
    poetry run python your_script.py
    ```

## Example Output

Here is an example of what the output looks like when the program runs successfully:

![Container Loading Visualization](path_to_your_image.png)

This project provides a comprehensive solution for visualizing and managing the loading of containers, ensuring optimal use of space and weight capacity.
