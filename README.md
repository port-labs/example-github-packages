# Getting started
In this example, you will create a blueprint for `githubPackage` that ingests Github Packages from your GitHub organization into Port. You will then use a Python script to make API calls to GitHub REST API to fetch the data from your account.

## Blueprints
Create the following blueprints in Port using the schemas:


### Package
Python Script for Ingesting Github Packages in Port

```json
{
  "identifier": "githubPackage",
  "description": "This blueprint represents a GitHub package in our software catalog",
  "title": "Github Package",
  "icon": "Github",
  "schema": {
    "properties": {
      "packageType": {
        "type": "string",
        "title": "Package Type",
        "enum": [
          "npm",
          "maven",
          "rubygems",
          "docker",
          "nuget",
          "container"
        ]
      },
      "visibility": {
        "type": "string",
        "title": "Visibility",
        "enum": [
          "public",
          "private",
          "internal"
        ]
      },
      "createdAt": {
        "type": "string",
        "title": "Created At",
        "format": "date-time"
      },
      "link": {
        "type": "string",
        "title": "Link",
        "format": "url"
      },
      "latestVersionTag": {
        "title": "Latest Version Tags",
        "type": "array"
      },
      "latestVersionCreatedAt": {
        "type": "string",
        "title": "Latest Version Created At",
        "format": "date-time"
      },
      "latestVersionLink": {
        "title": "Latest Version Link",
        "type": "string",
        "format": "url"
      }
    },
    "required": []
  },
  "mirrorProperties": {},
  "calculationProperties": {},
  "relations": {}
}
```

## Running the Python script
First clone the repository and cd into the work directory with:
```bash
$ git clone https://github.com/port-labs/example-github-packages.git
$ cd example-github-packages
```

Install the needed dependencies within the context of a virtual environment with:
```bash
$ virtualenv venv
$ source venv/bin/activate
$ pip3 install -r requirements.txt
```

To ingest your data, you need to populate some environment variables. You can do that by either duplicating the `.example.env` file and renaming the copy as `.env`, then edit the values as needed; or run the commands below in your terminal:

```bash
export PORT_CLIENT_ID=port_client_id
export PORT_CLIENT_SECRET=port_client_secret
export GITHUB_ACCESS_TOKEN=token
export ORGANIZATION_NAME=organization_name
```

Then run the script with:
```bash
$ python app.py
```

Each variable required are:
- PORT_CLIENT_ID: Port Client ID
- PORT_CLIENT_SECRET: Port Client secret
- GITHUB_ACCESS_TOKEN: Github access token
- ORGANIZATION_NAME: Github organization name

You can get the Github access token by following the instructions on the [authentication section](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-personal-access-token-classic)