import requests
import csv
from collections import defaultdict
import configparser

import logging

log = logging.getLogger(__name__)

# API endpoint
package_search_url = (
    "{}/api/action/package_search?{}&sort=views_total%20desc&rows={}"
)
pakcage_show_url = "{}/api/action/package_show?id="
# Default query
query = "q=*:*"


def fetch_data(url):
    """
    Fetch data from the API.

    Args:
        url (str): The URL of the API endpoint.

    Returns:
        dict: The JSON response from the API.

    Raises:
        Exception: If the API request fails.

    """
    response = requests.get(url)
    log.info(f"API response status code: {response.status_code}")
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("Failed to fetch data from the API.")


def save_to_csv(data, config):
    """
    Save datasets grouped by organization to a CSV file.

    Args:
        data (dict): A dictionary containing datasets grouped by organization.
        config (dict): A dictionary containing configuration settings.

    Returns:
        None

    Raises:
        FileNotFoundError: If the output file specified in the configuration
        settings does not exist.

    """
    filename = config["default"].get("output_file")
    portal = config["default"].get("url")
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        # Define the CSV column headers
        writer.writerow(
            [
                "Organization",
                "Title",
                "URL",
                "Metadata Created",
                "Metadata Modified",
                "Views",
            ]
        )
        log.info("Writing data to CSV file")

        # Sort and write datasets by organization
        for org, datasets in data.items():
            for dataset in datasets:
                title = dataset["title"]
                url = portal + "/dataset/" + dataset["name"]
                metadata_created = dataset["metadata_created"]
                metadata_modified = dataset["metadata_modified"]
                views = get_dataset_views(dataset, config)
                writer.writerow(
                    [org, title, url, metadata_created, metadata_modified, views]
                )


def get_dataset_views(dataset, config):
    """Get the number of views for a dataset."""
    url = (
        pakcage_show_url.format(config["default"].get("url"))
        + dataset["id"]
        + "&include_tracking=True"
    )
    package = requests.get(url).json()
    log.info(f"Getting views for dataset {dataset['name']}")
    data = package["result"]
    return data.get("tracking_summary").get("total", 0)


def group_by_organization(data, organization=None):
    """Group datasets by their organization."""
    grouped_data = defaultdict(list)
    for dataset in data["result"]["results"]:
        org_name = dataset["organization"]["title"]
        org = dataset["organization"]["name"]
        if organization and org == organization:
            grouped_data[org_name].append(dataset)
    return grouped_data


def load(filename):
    """Load configuration from an INI file."""
    config = configparser.ConfigParser()
    config.read(filename)
    return config


def main():
    # loading log configuration
    logging.basicConfig(level=logging.INFO)
    # logging.config.fileConfig('logging.ini')
    config = load("config.ini")
    default = config["default"]
    if not default.get("url"):
        raise ValueError("No URL provided in the configuration file.")
    if not default.get("rows"):
        raise ValueError("No rows provided in the configuration file.")
    if not default.get("output_file"):
        raise ValueError("No output file provided in the configuration file.")
    # Construct the API URL
    org = default.get("organization") or None
    rows = default.get("rows")
    if org:
        url = package_search_url.format(
            default.get("url"), query + f"+organization:{org}", rows)
    else:
        url = package_search_url.format(default.get("url"), rows)
    # Fetch the dataset information
    log.info("Fetching data from the API")
    data = fetch_data(url)
    # Group datasets by organization
    log.info("Grouping datasets by organization")
    grouped_data = group_by_organization(data, default.get("organization"))
    # Save the information to a CSV file, grouped by organization
    log.info("Saving data to CSV file")
    save_to_csv(grouped_data, config)
    print("Data has been successfully saved to the file.")


if __name__ == "__main__":
    main()
