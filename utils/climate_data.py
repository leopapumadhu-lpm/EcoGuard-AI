# =============================================================================
# EcoGuard AI - Climate Data Utilities
# Fetches real long-term climate datasets from official public sources.
#
# Data sources:
#   Temperature  : NASA GISS Surface Temperature Analysis v4 (GISTEMP)
#                  https://data.giss.nasa.gov/gistemp/
#                  Annual mean anomaly relative to 1951–1980 baseline, 1880–present
#
#   Sea Ice      : NSIDC Sea Ice Index v4 — September minimum extent
#                  https://nsidc.org/data/seaice_index
#                  Annual September Arctic sea ice extent (million km²), 1979–present
#
#   Sea Level    : NOAA Laboratory for Satellite Altimetry — multi-mission GMSL
#                  https://www.star.nesdis.noaa.gov/socd/lsa/SeaLevelRise/
#                  Sub-monthly merged altimetry (TOPEX/Poseidon, Jason-1/2/3,
#                  Sentinel-6MF). Annual signals retained. 1993–present.
#                  Unit: mm above a 1993-baseline mean.
#
#   Forest Area  : FAOSTAT Land Use bulk dataset (FAO)
#                  https://fenixservices.fao.org/faostat/static/bulkdownloads/
#                  Item: Forest land (code 6646), World aggregate (area code 5000)
#                  Unit: 1 000 ha → converted to million ha on load. 1990–present.
#
# All functions are cached for 24 hours (ttl=86400) to avoid hammering upstream
# servers.  Every function returns None on any network or parse failure —
# callers must show a clear unavailable message; never show fake data.
# =============================================================================

import io
import zipfile

import pandas as pd
import requests
import streamlit as st


# ---------------------------------------------------------------------------
# Shared session for connection reuse
# ---------------------------------------------------------------------------
_SESSION = requests.Session()
_SESSION.headers.update({"User-Agent": "EcoGuard-AI/1.0 (educational project)"})


# ---------------------------------------------------------------------------
# Temperature — NASA GISS GISTEMP v4
# ---------------------------------------------------------------------------

@st.cache_data(ttl=86400)
def get_global_temperature_data() -> pd.DataFrame | None:
    """
    Fetch global mean surface temperature anomaly from NASA GISS GISTEMP v4.

    Source  : NASA Goddard Institute for Space Studies
    Dataset : GISTEMP v4 — GLB.Ts+dSST
    URL     : https://data.giss.nasa.gov/gistemp/tabledata_v4/GLB.Ts+dSST.csv

    Returns a DataFrame with columns:
        year    (int)   – calendar year
        anomaly (float) – annual mean anomaly in °C above 1951–1980 baseline

    Returns None on any network or parse error (caller must handle).
    """
    url = "https://data.giss.nasa.gov/gistemp/tabledata_v4/GLB.Ts+dSST.csv"
    try:
        resp = _SESSION.get(url, timeout=20)
        resp.raise_for_status()

        # The CSV has a one-line description header before the column names.
        df = pd.read_csv(
            io.StringIO(resp.text),
            header=1,
            na_values=["***", "****"],
        )

        # "J-D" is the Jan–Dec annual mean anomaly column.
        df = df[["Year", "J-D"]].dropna(subset=["J-D"])
        df.columns = ["year", "anomaly"]
        df["year"]    = pd.to_numeric(df["year"],    errors="coerce").dropna()
        df["anomaly"] = pd.to_numeric(df["anomaly"], errors="coerce")
        df = df.dropna().astype({"year": int}).sort_values("year").reset_index(drop=True)
        return df

    except Exception:
        return None


# ---------------------------------------------------------------------------
# Arctic Sea Ice — NSIDC Sea Ice Index v4 (September minimum)
# ---------------------------------------------------------------------------

@st.cache_data(ttl=86400)
def get_arctic_sea_ice_data() -> pd.DataFrame | None:
    """
    Fetch Arctic sea ice September minimum extent from NSIDC v4.

    Source  : National Snow and Ice Data Center (NSIDC) / NOAA
    Dataset : Sea Ice Index v4 — Northern Hemisphere September extent
    URL     : https://noaadata.apps.nsidc.org/NOAA/G02135/north/monthly/data/
              N_09_extent_v4.0.csv

    Returns a DataFrame with columns:
        year   (int)   – calendar year
        extent (float) – September sea ice extent in million km²

    Returns None on any network or parse error (caller must handle).
    """
    url = (
        "https://noaadata.apps.nsidc.org/NOAA/G02135/north/monthly/data/"
        "N_09_extent_v4.0.csv"
    )
    try:
        resp = _SESSION.get(url, timeout=20)
        resp.raise_for_status()

        df = pd.read_csv(io.StringIO(resp.text))

        # Column names have leading/trailing spaces — strip them all.
        df.columns = [c.strip() for c in df.columns]

        # Strip whitespace from string cell values too (source data quirk).
        df = df.map(lambda v: v.strip() if isinstance(v, str) else v)

        df = df[["year", "extent"]].copy()
        df["year"]   = pd.to_numeric(df["year"],   errors="coerce")
        df["extent"] = pd.to_numeric(df["extent"], errors="coerce")
        df = (
            df.dropna()
            .astype({"year": int})
            .sort_values("year")
            .reset_index(drop=True)
        )
        return df

    except Exception:
        return None


# ---------------------------------------------------------------------------
# Global Mean Sea Level — NOAA Laboratory for Satellite Altimetry
# ---------------------------------------------------------------------------

@st.cache_data(ttl=86400)
def get_global_sea_level_data() -> pd.DataFrame | None:
    """
    Fetch Global Mean Sea Level (GMSL) from NOAA Laboratory for Satellite
    Altimetry — merged multi-mission altimetry product.

    Source  : NOAA / Laboratory for Satellite Altimetry (LSA)
    Dataset : Mean Sea Level Anomaly, Global Ocean 66°S–66°N
              Annual signals retained; no glacial isostatic adjustment.
    URL     : https://www.star.nesdis.noaa.gov/socd/lsa/SeaLevelRise/slr/
              slr_sla_gbl_keep_all_66.csv

    Missions (sequential, merged into a single series):
        TOPEX/Poseidon (1993–2002), Jason-1 (2002–2008),
        Jason-2 (2008–2016), Jason-3 (2016–2022),
        Sentinel-6MF (2021–present)

    Returns a DataFrame with columns:
        year         (float) – decimal year (e.g. 1993.042)
        sea_level_mm (float) – GMSL anomaly in mm above 1993-baseline mean

    NOTE: This is NOT a real-time dataset. It is periodically updated by NOAA.
    Always refer to it as "latest available official data".

    Returns None on any network or parse error (caller must handle).
    """
    url = (
        "https://www.star.nesdis.noaa.gov/socd/lsa/SeaLevelRise/slr/"
        "slr_sla_gbl_keep_all_66.csv"
    )
    try:
        resp = _SESSION.get(url, timeout=25)
        resp.raise_for_status()

        # Skip comment lines (start with #)
        lines = [
            line for line in resp.text.splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]
        if not lines:
            return None

        df = pd.read_csv(
            io.StringIO("\n".join(lines)),
            sep=",",
            header=0,
            na_values=["99900.000", "99900", ""],
        )

        # Column layout: year, TOPEX/Poseidon, Jason-1, Jason-2, Jason-3, Sentinel-6MF
        # Each row has a value in exactly one mission column. Merge to one series.
        mission_cols = [c for c in df.columns if c != "year"]
        if not mission_cols:
            return None

        # Take the first non-NaN value across mission columns for each row.
        df["sea_level_mm"] = df[mission_cols].bfill(axis=1).iloc[:, 0]

        df = df[["year", "sea_level_mm"]].copy()
        df["year"]         = pd.to_numeric(df["year"],         errors="coerce")
        df["sea_level_mm"] = pd.to_numeric(df["sea_level_mm"], errors="coerce")
        df = (
            df.dropna()
            .sort_values("year")
            .drop_duplicates(subset=["year"])
            .reset_index(drop=True)
        )

        if df.empty:
            return None

        return df

    except Exception:
        return None


# ---------------------------------------------------------------------------
# Global Forest Area — FAOSTAT Land Use bulk dataset (FAO)
# ---------------------------------------------------------------------------

@st.cache_data(ttl=86400)
def get_global_forest_data() -> pd.DataFrame | None:
    """
    Fetch global forest land area from the FAOSTAT Land Use bulk dataset.

    Source  : Food and Agriculture Organization of the United Nations (FAO)
    Dataset : FAOSTAT — Inputs: Land Use
              Item code 6646 (Forest land), Area code 5000 (World aggregate),
              Element: Area
    URL     : https://fenixservices.fao.org/faostat/static/bulkdownloads/
              Inputs_LandUse_E_All_Data_(Normalized).zip

    The original unit is 1 000 ha.  This function converts to million hectares
    (divide by 1 000) so that values are in a human-readable range.

    Returns a DataFrame with columns:
        year        (int)   – calendar year
        forest_area (float) – global forest land area in million hectares

    Data range: typically 1990–present (latest FAO assessment year).

    NOTE: FAO updates this dataset periodically. Always refer to it as
    "latest available FAO data".

    Returns None on any network or parse error (caller must handle).
    """
    url = (
        "https://fenixservices.fao.org/faostat/static/bulkdownloads/"
        "Inputs_LandUse_E_All_Data_(Normalized).zip"
    )
    try:
        resp = _SESSION.get(url, timeout=60, stream=True)
        resp.raise_for_status()

        # Read the ZIP in memory
        zf = zipfile.ZipFile(io.BytesIO(resp.content))

        # The normalised CSV is always the first file and ends with '_Normalized).csv'
        csv_name = next(
            (n for n in zf.namelist() if n.endswith(".csv") and "Normalized" in n),
            zf.namelist()[0],
        )

        with zf.open(csv_name) as f:
            df = pd.read_csv(f, encoding="latin-1")

        # Filter: World aggregate (Area Code 5000) + Forest land (Item Code 6646)
        #         + Element "Area" (i.e. not the % share column)
        mask = (
            (df["Area Code"]   == 5000)
            & (df["Item Code"] == 6646)
            & (df["Element"]   == "Area")
        )
        df_forest = df.loc[mask, ["Year", "Value"]].copy()

        if df_forest.empty:
            return None

        df_forest.columns = ["year", "forest_area_1000ha"]
        df_forest["year"]            = pd.to_numeric(df_forest["year"],            errors="coerce")
        df_forest["forest_area_1000ha"] = pd.to_numeric(df_forest["forest_area_1000ha"], errors="coerce")
        df_forest = df_forest.dropna()

        # Convert 1 000 ha → million hectares  (÷ 1 000)
        df_forest["forest_area"] = df_forest["forest_area_1000ha"] / 1_000.0

        df_forest = (
            df_forest[["year", "forest_area"]]
            .astype({"year": int})
            .sort_values("year")
            .drop_duplicates(subset=["year"])
            .reset_index(drop=True)
        )

        if df_forest.empty:
            return None

        return df_forest

    except Exception:
        return None
