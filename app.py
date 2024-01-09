import asyncio
import os
from typing import Any
from urllib.parse import urlencode

import aiohttp
import dotenv
import requests
from loguru import logger

dotenv.load_dotenv()

PORT_API_URL = "https://api.getport.io/v1"
PORT_CLIENT_ID = os.getenv("PORT_CLIENT_ID")
PORT_CLIENT_SECRET = os.getenv("PORT_CLIENT_SECRET")
GITHUB_ACCESS_TOKEN = os.getenv("GITHUB_ACCESS_TOKEN")
ORGANIZATION_NAME = os.getenv("ORGANIZATION_NAME")
REPOSITORY_BLUEPRINT = "githubPackage"
PACKAGE_TYPES = ["npm", "maven", "rubygems", "docker", "nuget", "container"]
DEFAULT_PAGE_SIZE = 100
DEFAULT_PAGE_NUMBER = 1

## Get Port Access Token
credentials = {"clientId": PORT_CLIENT_ID, "clientSecret": PORT_CLIENT_SECRET}

token_response = requests.post(f"{PORT_API_URL}/auth/access_token", json=credentials)
access_token = token_response.json()["accessToken"]

# You can now use the value in access_token when making further requests
headers = {"Authorization": f"Bearer {access_token}"}


async def add_entity_to_port(
    session: aiohttp.ClientSession, blueprint_id, entity_object
):
    """A function to create the passed entity in Port

    Params
    --------------
    blueprint_id: str
        The blueprint id to create the entity in Port

    entity_object: dict
        The entity to add in your Port catalog

    Returns
    --------------
    response: dict
        The response object after calling the webhook
    """
    logger.info(f"Adding entity to Port: {entity_object}")
    response = await session.post(
        (
            f"{PORT_API_URL}/blueprints/"
            f"{blueprint_id}/entities?upsert=true&merge=true"
        ),
        json=entity_object,
        headers=headers,
    )
    if not response.ok:
        logger.info("Ingesting {blueprint_id} entity to port failed, skipping...")
    logger.info(f"Added entity to Port: {entity_object}")


async def get_github_packages(
    session: aiohttp.ClientSession, url: str, package_type: str
) -> list[dict[str, Any]]:
    """
    A function to get all the packages for a given repo

    Returns
    --------------
    packages: dict
        The packages for the given repo
    """
    query_params = {
        "package_type": package_type,
        "per_page": DEFAULT_PAGE_SIZE,
        "page": DEFAULT_PAGE_NUMBER,
    }
    logger.info(f"Getting packages")
    page_size = DEFAULT_PAGE_SIZE

    while page_size >= DEFAULT_PAGE_SIZE:
        logger.info(f"Retrieving page {query_params['page']} of packages for {package_type}")
        async with session.get(
            f"{url}/packages?{urlencode(query_params)}",
            headers={
                "Authorization": f"Bearer {GITHUB_ACCESS_TOKEN}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        ) as response:
            if not response.ok:
                logger.error(f"Error retrieving packages: {response.status} error")
                return

            packages: list[dict[str, Any]] = await response.json()
            page_size = len(packages)
            query_params["page"] += 1
            logger.info(f"Retrieved page for packages")
            yield packages


async def get_package_metadata(
    session: aiohttp.ClientSession, package: dict[str, Any]
) -> dict[str, Any]:
    """
    A function to get the metadata for a given package

    Returns
    --------------
    metadata: dict
        The metadata for the given package
    """
    logger.info(f"Getting package metadata for package: {package['name']}")
    async with session.get(
        f"{package['url']}/versions",
        headers={
            "Authorization": f"Bearer {GITHUB_ACCESS_TOKEN}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    ) as response:
        if not response.ok:
            logger.error(f"Error retrieving package metadata: {response.status} error")
            return None
        metadata: list[dict[str, Any]] = await response.json()
        logger.info(f"Retrieved package metadata for package: {package['name']}")
        return metadata[0]


async def ingest_package_into_port(
    session: aiohttp.ClientSession,
    package: dict[str, Any],
    package_metadata: dict[str, Any],
    package_type: str,
):
    package_blueprint = {
        "identifier": str(package["id"]),
        "title": package["name"],
        "properties": {
            "packageType": package_type,
            "visibility": package["visibility"],
            "createdAt": package["created_at"],
            "link": package["html_url"],
            "latestVersionTag": package_metadata["name"],
            "latestVersionLink": package_metadata["html_url"],
            "latestVersionCreatedAt": package_metadata["created_at"],
        },
    }

    await add_entity_to_port(session, REPOSITORY_BLUEPRINT, package_blueprint)


async def main():
    logger.info("Starting Port integration")
    url = f"https://api.github.com/orgs/{ORGANIZATION_NAME}"
    async with aiohttp.ClientSession() as session:
        for package_type in PACKAGE_TYPES:
            async for packages in get_github_packages(session, url, package_type):
                for package in packages:
                    package_metadata = await get_package_metadata(session, package)
                    if not package_metadata:
                        continue
                    await ingest_package_into_port(
                        session, package, package_metadata, package_type
                    )
    logger.info("Ingested all packages into Port")


if __name__ == "__main__":
    asyncio.run(main())
