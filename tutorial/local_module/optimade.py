"""A simple Optimade client."""

from __future__ import annotations

import json
import re
import warnings
from pathlib import Path
from typing import Literal, Optional, Sequence, TypedDict
from urllib.parse import urlencode

import pandas
import requests
from optimade.adapters.structures.aiida import get_aiida_structure_data
from optimade.adapters.warnings import ConversionWarning
from optimade.models import StructureResource


def get_providers(cache_file: Path | None = None) -> pandas.DataFrame:
    """Get the providers from the cache file."""
    if cache_file is None:
        cache_file = Path(__file__).parent / "optimade_providers.json"
    with open(cache_file) as f:
        providers = json.load(f)
    return pandas.DataFrame(providers).set_index("id")


def count_structures(provider: str, filter_str: str, timeout: int = 20) -> int:
    """Count the number of structures matching a filter."""
    providers = get_providers()
    base_url = providers.loc[provider, "base_url"]
    data = _perform_optimade_query(
        base_url,
        filter_str=filter_str,
        page_limit=1,
        timeout=timeout,
        response_fields="",
    )
    return data["meta"]["data_returned"]


def yield_structures(
    provider: str, filter_str: str, batch: int = 1, timeout: int = 20, max_results=None
):
    """Yield structures from a provider.

    :param provider: The provider ID to query.
    :param filter: The filter to apply (see https://github.com/Materials-Consortia/OPTIMADE/blob/master/optimade.rst#the-filter-language-syntax).
    :param timeout: The timeout for URL requests.
    :param max_results: The maximum number of results to yield.
    """
    providers = get_providers()
    base_url = providers.loc[provider, "base_url"]
    offset = 0
    while True:
        data = _perform_optimade_query(
            base_url,
            filter_str=filter_str,
            page_limit=batch,
            page_offset=offset,
            timeout=timeout,
        )
        for entry in data["data"]:
            # filter warning ConversionWarning
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", ConversionWarning)
                structure = get_aiida_structure_data(StructureResource(**entry))
            yield structure
            offset += 1
            if max_results is not None and offset >= max_results:
                return
        if not data["meta"]["more_data_available"]:
            break


def _perform_optimade_query(  # pylint: disable=too-many-arguments,too-many-branches,too-many-locals
    base_url: str,
    endpoint: str = None,
    filter_str: str = "",
    sort: str | list[str] = None,
    response_format: Optional[str] = None,
    response_fields: Optional[str] = None,
    email_address: Optional[str] = None,
    page_limit: Optional[int] = 1,
    page_offset: Optional[int] = None,
    page_number: Optional[int] = None,
    timeout: int = 10,
) -> dict:
    """Perform query of database"""
    queries = {}

    if endpoint is None:
        endpoint = "/structures"
    elif endpoint:
        # Make sure we supply the correct slashed format no matter the input
        endpoint = f"/{endpoint.strip('/')}"

    url_path = (
        base_url + endpoint[1:] if base_url.endswith("/") else base_url + endpoint
    )

    if filter_str:
        if isinstance(filter_str, str):
            queries["filter"] = filter_str
        else:
            raise TypeError("'filter_str' must be either a dict or a str")

    if sort is not None:
        if isinstance(sort, str):
            queries["sort"] = sort
        else:
            queries["sort"] = ",".join(sort)

    if response_format is None:
        response_format = "json"
    queries["response_format"] = response_format

    if response_fields is not None:
        queries["response_fields"] = response_fields
    elif endpoint == "/structures":
        queries["response_fields"] = ",".join(
            [
                "structure_features",
                "chemical_formula_anonymous",
                "chemical_formula_descriptive",
                "chemical_formula_hill",
                "chemical_formula_reduced",
                "elements",
                "nsites",
                "lattice_vectors",
                "species",
                "cartesian_site_positions",
                "species_at_sites",
                "nelements",
                "nperiodic_dimensions",
                "last_modified",
                "elements_ratios",
                "dimension_types",
            ]
        )

    if email_address is not None:
        queries["email_address"] = email_address

    if page_limit is not None:
        queries["page_limit"] = page_limit

    if page_offset is not None:
        queries["page_offset"] = page_offset

    if page_number is not None:
        queries["page_number"] = page_number

    # Make query - get data
    url_query = urlencode(queries)
    complete_url = f"{url_path}?{url_query}"
    # LOGGER.debug("Performing OPTIMADE query:\n%s", complete_url)
    try:
        response = requests.get(complete_url, timeout=timeout)
        # if response.from_cache:
        #     LOGGER.debug("Request to %s was taken from cache !", complete_url)
    except (
        requests.exceptions.ConnectTimeout,
        requests.exceptions.ConnectionError,
        requests.exceptions.ReadTimeout,
    ) as exc:
        raise Exception(
            f"CLIENT: Connection error or timeout.\nURL: {complete_url}\n"
            f"Exception: {exc!r}"
        )

    try:
        data = response.json()
    except json.JSONDecodeError as exc:
        raise Exception(
            f"CLIENT: Cannot decode response to JSON format.\nURL: {complete_url}\n"
            f"Exception: {exc!r}"
        )

    return data


class LinkAttributes(TypedDict):
    """Link attributes"""

    name: str
    description: str
    base_url: None | str | dict
    homepage: Optional[str]
    link_type: Literal["child", "root", "external", "providers"]
    aggregate: Optional[Literal["ok", "test", "staging", "no"]]


class LinkResource(TypedDict):
    """OPTIMADE link resource"""

    id: str
    type: str
    attributes: LinkAttributes


class Providers(TypedDict):
    """OPTIMADE providers"""

    id: str
    name: str
    description: str
    base_url: str
    homepage: str


def _get_versioned_base_url(  # pylint: disable=too-many-branches
    base_url: str | dict,
    timeout: int = 10,
    version_endpoints: Sequence[str] = (
        "/v1",
        "/v1.1",
        "/v1.1.0",
        "/v1",
        "/v1.0",
        "/v1.0.1",
        "/v1",
        "/v1.0",
        "/v1.0.0",
    ),
) -> str:
    """Retrieve the versioned base URL

    First, check if the given base URL is already a versioned base URL.

    Then, use `Version Negotiation` as outlined in the specification:
    https://github.com/Materials-Consortia/OPTIMADE/blob/v1.0.0/optimade.rst#version-negotiation

    1. Try unversioned base URL's `/versions` endpoint.
    2. Go through valid versioned base URLs.

    """
    if isinstance(base_url, dict):
        base_url = base_url.get("href", "")

    for version in version_endpoints:
        if version in base_url:
            if re.match(rf".+{version}$", base_url):
                return base_url
            if re.match(rf".+{version}/$", base_url):
                return base_url[:-1]
            # LOGGER.debug(
            #     "Found version '%s' in base URL '%s', but not at the end of it. Will continue.",
            #     version,
            #     base_url,
            # )

    # 1. Try unversioned base URL's `/versions` endpoint.
    versions_endpoint = (
        f"{base_url}versions" if base_url.endswith("/") else f"{base_url}/versions"
    )
    try:
        response = requests.get(versions_endpoint, timeout=timeout)
        # if response.from_cache:
        #     LOGGER.debug("Request to %s was taken from cache !", versions_endpoint)
    except (
        requests.exceptions.ConnectTimeout,
        requests.exceptions.ConnectionError,
        requests.exceptions.ReadTimeout,
    ):
        pass
    else:
        if response.status_code == 200:
            # This endpoint should be of type "text/csv"
            csv_data = response.text.splitlines()
            if not csv_data:
                return ""
            keys = csv_data.pop(0).split(",")
            versions = {}.fromkeys(keys, [])
            for line in csv_data:
                values = line.split(",")
                for key, value in zip(keys, values):
                    versions[key].append(value)

            for version in versions.get("version", []):
                version_path = f"/v{version}"
                if version_path in version_endpoints:
                    # LOGGER.debug("Found versioned base URL through /versions endpoint.")
                    return (
                        base_url + version_path[1:]
                        if base_url.endswith("/")
                        else base_url + version_path
                    )

    timeout_seconds = 5  # Use custom timeout seconds due to potentially many requests

    # 2. Go through valid versioned base URLs.
    for version in version_endpoints:
        versioned_base_url = (
            base_url + version[1:] if base_url.endswith("/") else base_url + version
        )
        try:
            response = requests.get(
                f"{versioned_base_url}/info", timeout=timeout_seconds
            )
            # if response.from_cache:
            #     LOGGER.debug(
            #         "Request to %s/info was taken from cache !", versioned_base_url
            #     )
        except (
            requests.exceptions.ConnectTimeout,
            requests.exceptions.ConnectionError,
            requests.exceptions.ReadTimeout,
        ):
            continue
        else:
            if response.status_code == 200:
                # LOGGER.debug(
                #     "Found versioned base URL through adding valid versions to path and requesting "
                #     "the /info endpoint."
                # )
                return versioned_base_url

    return ""


def _fetch_providers(
    providers_urls: Sequence[str] = (
        "https://providers.optimade.org/v1/links",
        "https://raw.githubusercontent.com/Materials-Consortia/providers/master/src"
        "/links/v1/providers.json",
    )
) -> list[Providers]:
    """Fetch OPTIMADE database providers (from Materials-Consortia)

    :param providers_urls: String or list of strings with versioned base URL(s)
        to Materials-Consortia providers database
    """
    for providers_url in providers_urls:
        response = _perform_optimade_query(base_url=providers_url, endpoint="")
        if ("data" not in response and "errors" not in response) or (
            "errors" in response
        ):
            continue
        break
    else:
        raise RuntimeError("no valid providers found")

    providers: list[LinkResource] = response["data"]
    ok_providers: list[LinkResource] = []
    for provider in providers:
        attributes = provider["attributes"]
        if attributes["link_type"] != "external":
            continue
        if attributes["base_url"] is None:
            continue
        versioned_base_url = _get_versioned_base_url(attributes["base_url"])
        if not versioned_base_url:
            continue
        attributes["base_url"] = versioned_base_url
        ok_providers.append(provider)

    links: list[Providers] = []
    for provider in ok_providers:
        filter_ = '( link_type="child" OR type="child" )'
        response = _perform_optimade_query(
            provider["attributes"]["base_url"], "/links", filter=filter_
        )
        implementations = [
            implementation
            for implementation in response.get("data", [])
            if (
                (
                    implementation.get("attributes", {}).get("link_type", "") == "child"
                    or implementation.get("type", "") == "child"
                )
                and implementation.get("attributes", {}).get("base_url", "")
            )
        ]
        for imp in implementations:
            versioned_base_url = _get_versioned_base_url(imp["attributes"]["base_url"])
            if not versioned_base_url:
                continue
            links.append(
                {
                    "id": imp["id"],
                    "name": imp["attributes"]["name"],
                    "description": imp["attributes"]["description"],
                    "base_url": versioned_base_url,
                    "homepage": imp["attributes"]["homepage"],
                }
            )

    return links


def update_provider_cache(cache_file: Path | None = None):
    """Update the provider cache file."""
    if cache_file is None:
        cache_file = Path(__file__).parent / "optimade_providers.json"
    providers = _fetch_providers()
    with open(cache_file, "w") as f:
        json.dump(providers, f, indent=2)
