"""
Data Loader utility.
Loads and caches synthetic JSON datasets for EHR, Pharmacy, and Billing.
"""
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

# Base data directory
DATA_DIR = Path(__file__).parent.parent.parent / "data"


class DataLoader:
    """
    Centralized data loader for all synthetic JSON datasets.
    Provides cached access to EHR, Pharmacy, and Billing data.
    """

    _ehr_data: Optional[Dict] = None
    _pharmacy_data: Optional[Dict] = None
    _billing_data: Optional[Dict] = None

    @classmethod
    def _load_json(cls, path: Path) -> Dict:
        """Load a JSON file."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Data file not found: {path}")
            raise FileNotFoundError(f"Data file not found: {path}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {path}: {e}")
            raise ValueError(f"Invalid JSON in data file: {path}")

    @classmethod
    def get_ehr_data(cls) -> Dict:
        """Get EHR data (cached)."""
        if cls._ehr_data is None:
            cls._ehr_data = cls._load_json(DATA_DIR / "ehr" / "synthetic_records.json")
            logger.info(f"Loaded EHR data: {len(cls._ehr_data.get('patients', []))} patients")
        return cls._ehr_data

    @classmethod
    def get_pharmacy_data(cls) -> Dict:
        """Get Pharmacy data (cached)."""
        if cls._pharmacy_data is None:
            cls._pharmacy_data = cls._load_json(DATA_DIR / "pharmacy" / "synthetic_pharmacy_records.json")
            logger.info(f"Loaded Pharmacy data: {len(cls._pharmacy_data.get('inventory', []))} items")
        return cls._pharmacy_data

    @classmethod
    def get_billing_data(cls) -> Dict:
        """Get Billing data (cached)."""
        if cls._billing_data is None:
            cls._billing_data = cls._load_json(DATA_DIR / "billing" / "synthetic_billing_records.json")
            logger.info(f"Loaded Billing data: {len(cls._billing_data.get('billing_codes', []))} codes")
        return cls._billing_data

    @classmethod
    def get_all_patients(cls) -> List[Dict]:
        """Get list of all patients."""
        return cls.get_ehr_data().get("patients", [])

    @classmethod
    def get_patient_by_id(cls, patient_id: str) -> Optional[Dict]:
        """Find a patient by ID."""
        patients = cls.get_all_patients()
        pid = patient_id.strip().upper()
        for p in patients:
            if p["patient_id"].upper() == pid:
                return p
        return None

    @classmethod
    def get_inventory(cls) -> List[Dict]:
        """Get pharmacy inventory."""
        return cls.get_pharmacy_data().get("inventory", [])

    @classmethod
    def get_inventory_item(cls, generic_name: str) -> Optional[Dict]:
        """Find an inventory item by generic name."""
        gname = generic_name.strip().lower()
        for item in cls.get_inventory():
            if item["generic_name"].lower() == gname:
                return item
        return None

    @classmethod
    def get_brand_to_generic_map(cls) -> Dict:
        """Get brand-to-generic mapping."""
        return cls.get_pharmacy_data().get("brand_to_generic_map", {})

    @classmethod
    def resolve_brand(cls, brand_name: str) -> Optional[Dict]:
        """Resolve a brand name to generic info."""
        mapping = cls.get_brand_to_generic_map()
        # Case-insensitive lookup
        for brand, info in mapping.items():
            if brand.lower() == brand_name.strip().lower():
                return {"brand": brand, **info}
        return None

    @classmethod
    def get_alternatives(cls) -> List[Dict]:
        """Get alternative medicine mappings."""
        return cls.get_pharmacy_data().get("alternatives", [])

    @classmethod
    def get_alternatives_for(cls, generic_name: str) -> Optional[Dict]:
        """Get alternatives for a specific generic medicine."""
        gname = generic_name.strip().lower()
        for alt in cls.get_alternatives():
            if alt["for_generic"].lower() == gname:
                return alt
        return None

    @classmethod
    def get_allergy_rules(cls) -> List[Dict]:
        """Get allergy conflict rules."""
        return cls.get_pharmacy_data().get("allergy_conflict_rules", [])

    @classmethod
    def get_billing_codes(cls) -> List[Dict]:
        """Get billing codes."""
        return cls.get_billing_data().get("billing_codes", [])

    @classmethod
    def get_billing_code(cls, code: str) -> Optional[Dict]:
        """Find a billing code."""
        for bc in cls.get_billing_codes():
            if bc["code"].upper() == code.strip().upper():
                return bc
        return None

    @classmethod
    def get_drug_catalog(cls) -> List[Dict]:
        """Get drug catalog."""
        return cls.get_billing_data().get("drug_catalog", [])

    @classmethod
    def get_drug_catalog_entry(cls, generic_name: str) -> Optional[Dict]:
        """Find a drug catalog entry by generic name."""
        gname = generic_name.strip().lower()
        for entry in cls.get_drug_catalog():
            if entry["generic_name"].lower() == gname:
                return entry
        return None

    @classmethod
    def get_service_charges(cls) -> Dict:
        """Get service charges."""
        return cls.get_billing_data().get("service_charges", {})

    @classmethod
    def reload_all(cls):
        """Force reload all cached data."""
        cls._ehr_data = None
        cls._pharmacy_data = None
        cls._billing_data = None
        cls.get_ehr_data()
        cls.get_pharmacy_data()
        cls.get_billing_data()
        logger.info("All data reloaded from files")


# Singleton data loader
data_loader = DataLoader()
