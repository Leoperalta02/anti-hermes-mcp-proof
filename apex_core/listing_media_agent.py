"""
Apex Luxury AI — Listing & Media Intake Agent
Per CURSOR_MISSION_LISTING_AGENT.md, ROSIE_ONBOARDING_SOP.md §8 & §12.

Handles property media ingestion (photos, videos, specs, For Sale / Under Contract / Sold),
enriches with Keystone valuation benchmarks ($/sqft) and Quill luxury Florida copywriting,
and stages properties into office_listings.json for the kinetic Apple showcase.
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

DEFAULT_LISTINGS_PATH = Path(__file__).resolve().parent / "office_listings.json"
DEFAULT_QUEUE_PATH = Path(__file__).resolve().parent / "listing_intake_queue.json"
DEFAULT_TENANTS_ROOT = Path(r"C:\LEO-LAB-ANTIGRAVITY\hermes-state\profiles\real-estate-copilot\tenants")
DEFAULT_TENANT_SLUG = "rosie"

SECRET_RE = re.compile(
    r"(password|passwd|api[_-]?key|secret|token|bearer|authorization|"
    r"connection string|private[_-]?key)",
    re.IGNORECASE,
)

VALID_STATUSES = frozenset({"FOR_SALE", "UNDER_CONTRACT", "RECORD_SOLD"})

STATUS_DISPLAY: Dict[str, Tuple[str, str, str]] = {
    "FOR_SALE": ("for_sale", "✨ FOR SALE", "status-for-sale"),
    "UNDER_CONTRACT": ("under_contract", "⚡ UNDER CONTRACT", "status-pending"),
    "RECORD_SOLD": ("sold", "🏆 SOLD", "status-sold"),
}

# Keystone subdivision $/sqft benchmark tiers (Estero & Naples corridor)
SUBDIVISION_BENCHMARKS: Dict[str, Tuple[int, int]] = {
    "pelican sound": (310, 340),
    "pelican landing": (340, 380),
    "west bay club": (480, 550),
    "shadow wood": (420, 480),
    "vanderbilt beach": (780, 1200),
    "naples": (780, 1200),
    "estero": (310, 340),
}

DEFAULT_CLAIMS: Dict[str, bool] = {
    "agent_deployed": False,
    "portal_created": False,
    "mls_connected": False,
    "published_live": False,
    "voice_enabled": False,
    "calendar_synced": False,
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def format_currency(amount: float) -> str:
    return f"${amount:,.0f}"


def slugify_listing_id(text: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return cleaned[:48] or "listing"


@dataclass
class PropertyListingMedia:
    listing_id: str
    title: str
    address: str
    subdivision: str
    price: float
    status: str
    specs: Dict[str, Any]
    photos: List[str]
    video_url: Optional[str] = None
    tenant_slug: str = DEFAULT_TENANT_SLUG
    submitted_at: str = field(default_factory=utc_now_iso)


class ListingMediaAgent:
    """Listing & Media Intake Engine with Keystone/Quill enrichment and showcase staging."""

    def __init__(
        self,
        listings_path: Optional[Path] = None,
        tenant_dir: Optional[Path] = None,
        queue_path: Optional[Path] = None,
    ):
        self.listings_path = Path(listings_path) if listings_path else DEFAULT_LISTINGS_PATH
        self.queue_path = Path(queue_path) if queue_path else DEFAULT_QUEUE_PATH
        if tenant_dir:
            self.tenant_dir = Path(tenant_dir)
        else:
            self.tenant_dir = DEFAULT_TENANTS_ROOT / DEFAULT_TENANT_SLUG

    def _load_queue(self) -> List[Dict[str, Any]]:
        if not self.queue_path.exists():
            return []
        try:
            data = json.loads(self.queue_path.read_text(encoding="utf-8"))
            if isinstance(data, list):
                return data
        except Exception:
            pass
        return []

    def _write_queue(self, entries: List[Dict[str, Any]]) -> None:
        self.queue_path.parent.mkdir(parents=True, exist_ok=True)
        self.queue_path.write_text(json.dumps(entries, indent=2), encoding="utf-8")

    def load_intake_queue(self, tenant_slug: Optional[str] = None, pending_only: bool = True) -> List[Dict[str, Any]]:
        """Return queued intake entries, optionally filtered by tenant and pending status."""
        entries = self._load_queue()
        if tenant_slug:
            slug = tenant_slug.strip().lower()
            entries = [e for e in entries if str(e.get("listing", {}).get("tenant_slug", DEFAULT_TENANT_SLUG)).lower() == slug]
        if pending_only:
            entries = [e for e in entries if e.get("queue_status") == "PENDING_APPROVAL"]
        return entries

    def get_queue_entry(self, listing_id: str) -> Optional[Dict[str, Any]]:
        for entry in self._load_queue():
            if entry.get("listing_id") == listing_id:
                return entry
        return None

    def _reject_secrets(self, payload: Dict[str, Any]) -> None:
        payload_str = json.dumps(payload)
        if SECRET_RE.search(payload_str):
            raise ValueError(
                "[STOP — SECRET DETECTED] Submission contains credential-like content. "
                "Remove passwords, API keys, tokens, or secrets per SOP §12."
            )

    def _validate_required_fields(self, payload: Dict[str, Any]) -> None:
        required = ("title", "address", "price", "status")
        missing = [k for k in required if not str(payload.get(k, "")).strip()]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")

        photos = payload.get("photos") or payload.get("media") or []
        if not photos or not isinstance(photos, list) or not any(str(p).strip() for p in photos):
            raise ValueError("At least one photo or media path/URL is required.")

        status = str(payload["status"]).strip().upper()
        if status not in VALID_STATUSES:
            raise ValueError(
                f"Invalid status '{payload['status']}'. Must be one of: {sorted(VALID_STATUSES)}"
            )

    def ingest_property_submission(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and normalize a realtor property media submission."""
        self._reject_secrets(payload)
        self._validate_required_fields(payload)

        title = str(payload["title"]).strip()
        address = str(payload["address"]).strip()
        subdivision = str(payload.get("subdivision") or payload.get("neighborhood") or "Estero, FL").strip()
        price = float(payload["price"])
        status = str(payload["status"]).strip().upper()
        specs = dict(payload.get("specs") or {})
        photos = [str(p).strip() for p in (payload.get("photos") or payload.get("media") or []) if str(p).strip()]
        video_url = payload.get("video_url")
        tenant_slug = str(payload.get("tenant_slug") or DEFAULT_TENANT_SLUG).strip().lower()

        listing_id = str(payload.get("listing_id") or slugify_listing_id(f"{subdivision}-{address}"))

        listing = PropertyListingMedia(
            listing_id=listing_id,
            title=title,
            address=address,
            subdivision=subdivision,
            price=price,
            status=status,
            specs=specs,
            photos=photos,
            video_url=str(video_url).strip() if video_url else None,
            tenant_slug=tenant_slug,
            submitted_at=str(payload.get("submitted_at") or utc_now_iso()),
        )

        return {
            "status": "INGEST_ACCEPTED",
            "listing": asdict(listing),
            "claims": dict(DEFAULT_CLAIMS),
            "external_send_blocked": True,
            "timestamp": utc_now_iso(),
        }

    def _resolve_subdivision_benchmark(self, subdivision: str) -> Tuple[int, int]:
        sub_lower = subdivision.lower()
        for key, band in SUBDIVISION_BENCHMARKS.items():
            if key in sub_lower:
                return band
        return (310, 340)

    def enrich_with_specialists(self, listing: PropertyListingMedia) -> Dict[str, Any]:
        """Run Keystone valuation benchmark and Quill luxury copywriting enrichment."""
        sqft = float(listing.specs.get("sqft") or listing.specs.get("living_sqft") or 0)
        beds = listing.specs.get("beds", "—")
        baths = listing.specs.get("baths", "—")
        pool = listing.specs.get("pool", False)
        view = listing.specs.get("view") or listing.specs.get("waterfront") or "preserve views"

        price_per_sqft_val = round(listing.price / sqft, 2) if sqft > 0 else 0.0
        benchmark_low = round(listing.price * 0.95, 0)
        benchmark_high = round(listing.price * 1.05, 0)
        sub_low, sub_high = self._resolve_subdivision_benchmark(listing.subdivision)

        keystone_payload = {
            "listing_id": listing.listing_id,
            "address": listing.address,
            "subdivision": listing.subdivision,
            "list_price": listing.price,
            "sqft": sqft,
            "price_per_sqft": price_per_sqft_val,
            "price_per_sqft_display": f"${price_per_sqft_val:,.0f}/sqft" if sqft else "N/A",
            "comp_spread": {
                "low": benchmark_low,
                "high": benchmark_high,
                "display": f"{format_currency(benchmark_low)} - {format_currency(benchmark_high)}",
                "tolerance_pct": 5,
            },
            "subdivision_benchmark": {
                "low_per_sqft": sub_low,
                "high_per_sqft": sub_high,
                "display": f"${sub_low} – ${sub_high} / sq.ft",
            },
            "status": "DRAFT_PENDING_APPROVAL",
            "generated_at": utc_now_iso(),
            "claims": dict(DEFAULT_CLAIMS),
        }

        lifestyle_bits: List[str] = []
        if pool:
            lifestyle_bits.append("resort-caliber heated pool and extended lanai")
        if "golf" in str(view).lower() or "fairway" in str(view).lower():
            lifestyle_bits.append("championship golf vistas")
        if any(k in listing.subdivision.lower() for k in ("gulf", "beach", "water", "canal", "bay")):
            lifestyle_bits.append("Gulf-access sunsets and coastal breezes")
        else:
            lifestyle_bits.append("Southwest Florida golden-hour sunsets")

        lifestyle_phrase = ", ".join(lifestyle_bits) if lifestyle_bits else "Southwest Florida architectural lifestyle"

        quill_body = (
            f"# Quill Listing Narrative — {listing.title}\n\n"
            f"- Listing ID: `{listing.listing_id}`\n"
            f"- Status: DRAFT_PENDING_APPROVAL (Zero external send)\n"
            f"- Generated: {utc_now_iso()}\n\n"
            f"## Apple-Style Kinetic Narrative\n\n"
            f"**{listing.title}** unfolds as a masterwork of Florida luxury living in "
            f"{listing.subdivision}. {beds} bedrooms and {baths} baths frame "
            f"{f'{int(sqft):,}' if sqft else 'generous'} square feet of refined indoor-outdoor flow — "
            f"impact-glass sliders dissolve into an expansive lanai where {lifestyle_phrase} "
            f"become part of daily life.\n\n"
            f"Keystone benchmarks this residence at **{keystone_payload['price_per_sqft_display']}**, "
            f"positioned within a **±5% comp corridor** of "
            f"**{keystone_payload['comp_spread']['display']}**. "
            f"Quill copy is staged for realtor approval before any MLS or public publish.\n"
        )

        tenant_base = self.tenant_dir
        if listing.tenant_slug != DEFAULT_TENANT_SLUG:
            tenant_base = tenant_base.parent / listing.tenant_slug

        quill_dir = tenant_base / "quill" / "listings"
        keystone_dir = tenant_base / "keystone"
        quill_dir.mkdir(parents=True, exist_ok=True)
        keystone_dir.mkdir(parents=True, exist_ok=True)

        quill_path = quill_dir / f"{listing.listing_id}.md"
        keystone_path = keystone_dir / f"valuation_{listing.listing_id}.json"

        quill_path.write_text(quill_body, encoding="utf-8")
        keystone_path.write_text(json.dumps(keystone_payload, indent=2), encoding="utf-8")

        tagline = (
            f"Modern Florida luxury in {listing.subdivision} with "
            f"{lifestyle_bits[0] if lifestyle_bits else 'architectural indoor-outdoor living'}."
        )

        return {
            "status": "ENRICHMENT_STAGED",
            "listing_id": listing.listing_id,
            "keystone": keystone_payload,
            "quill_narrative": quill_body.split("## Apple-Style Kinetic Narrative\n\n", 1)[-1].strip(),
            "tagline": tagline,
            "quill_path": str(quill_path),
            "keystone_path": str(keystone_path),
            "claims": dict(DEFAULT_CLAIMS),
            "timestamp": utc_now_iso(),
        }

    def _build_showcase_entry(self, listing_data: Dict[str, Any]) -> Dict[str, Any]:
        listing = listing_data.get("listing") or listing_data
        enrichment = listing_data.get("enrichment") or {}

        status_key = str(listing.get("status", "FOR_SALE")).upper()
        showcase_status, status_label, status_pill_class = STATUS_DISPLAY.get(
            status_key, STATUS_DISPLAY["FOR_SALE"]
        )

        specs = listing.get("specs") or {}
        photos = listing.get("photos") or []
        keystone = enrichment.get("keystone") or listing_data.get("keystone") or {}

        price_raw = float(listing.get("price") or 0)
        sqft = specs.get("sqft") or specs.get("living_sqft")

        keystone_valuation = {
            "price_per_sqft": keystone.get("price_per_sqft_display", "N/A"),
            "benchmark_spread": keystone.get("comp_spread", {}).get("display", "Pending"),
            "market_velocity": f"Draft — {listing.get('subdivision', 'Estero')} corridor",
        }

        return {
            "id": listing.get("listing_id") or listing.get("id"),
            "title": listing.get("title"),
            "neighborhood": f"{listing.get('subdivision')}, Estero, FL",
            "submarket": listing.get("subdivision"),
            "address": listing.get("address"),
            "price": format_currency(price_raw),
            "price_raw": int(price_raw),
            "status": showcase_status,
            "status_label": status_label,
            "status_pill_class": status_pill_class,
            "workflow_status": "DRAFT_PENDING_APPROVAL",
            "beds": specs.get("beds"),
            "baths": str(specs.get("baths", "")),
            "sqft": sqft,
            "garage": specs.get("garage"),
            "lot": specs.get("lot"),
            "waterfront": specs.get("view") or specs.get("waterfront"),
            "primary_image": photos[0] if photos else None,
            "gallery": photos,
            "video_url": listing.get("video_url"),
            "tagline": enrichment.get("tagline") or listing.get("tagline", ""),
            "quill_narrative": enrichment.get("quill_narrative") or listing.get("quill_narrative", ""),
            "keystone_valuation": keystone_valuation,
            "tenant_slug": listing.get("tenant_slug", DEFAULT_TENANT_SLUG),
            "submitted_at": listing.get("submitted_at"),
            "claims": dict(DEFAULT_CLAIMS),
        }

    def stage_for_showcase(self, listing_data: Dict[str, Any]) -> Path:
        """Merge listing into office_listings.json for FastSiteBuilder.load_listings() compatibility."""
        entry = self._build_showcase_entry(listing_data)
        entry["claims"]["mls_connected"] = False
        entry["claims"]["published_live"] = False

        existing: List[Dict[str, Any]] = []
        if self.listings_path.exists():
            try:
                loaded = json.loads(self.listings_path.read_text(encoding="utf-8"))
                if isinstance(loaded, list):
                    existing = loaded
            except Exception:
                existing = []

        entry_id = entry.get("id")
        updated = False
        for idx, item in enumerate(existing):
            if item.get("id") == entry_id:
                existing[idx] = entry
                updated = True
                break
        if not updated:
            existing.append(entry)

        self.listings_path.parent.mkdir(parents=True, exist_ok=True)
        self.listings_path.write_text(json.dumps(existing, indent=2), encoding="utf-8")
        return self.listings_path

    def process_intake_submission(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Ingest + enrich and stage to intake queue (awaiting realtor approval for showcase)."""
        ingest_result = self.ingest_property_submission(payload)
        listing = PropertyListingMedia(**ingest_result["listing"])
        enrichment = self.enrich_with_specialists(listing)

        queue_entry = {
            "listing_id": listing.listing_id,
            "queue_status": "PENDING_APPROVAL",
            "listing": ingest_result["listing"],
            "enrichment": enrichment,
            "keystone": enrichment["keystone"],
            "claims": dict(DEFAULT_CLAIMS),
            "external_send_blocked": True,
            "send_gate": "LEO_AND_REALTOR_APPROVAL_REQUIRED",
            "submitted_at": listing.submitted_at,
            "approved_at": None,
        }

        entries = self._load_queue()
        replaced = False
        for idx, item in enumerate(entries):
            if item.get("listing_id") == listing.listing_id:
                entries[idx] = queue_entry
                replaced = True
                break
        if not replaced:
            entries.append(queue_entry)
        self._write_queue(entries)

        return {
            "status": "QUEUE_STAGED",
            "listing_id": listing.listing_id,
            "queue_path": str(self.queue_path),
            "quill_path": enrichment["quill_path"],
            "keystone_path": enrichment["keystone_path"],
            "claims": dict(DEFAULT_CLAIMS),
            "external_send_blocked": True,
            "send_gate": "LEO_AND_REALTOR_APPROVAL_REQUIRED",
            "timestamp": utc_now_iso(),
        }

    def approve_for_showcase(self, listing_id: str) -> Dict[str, Any]:
        """Promote a queued listing into office_listings.json after realtor approval."""
        entry = self.get_queue_entry(listing_id)
        if not entry:
            raise ValueError(f"Listing '{listing_id}' not found in intake queue.")

        if entry.get("queue_status") == "APPROVED_FOR_SHOWCASE":
            return {
                "status": "ALREADY_APPROVED",
                "listing_id": listing_id,
                "showcase_path": str(self.listings_path),
                "claims": dict(DEFAULT_CLAIMS),
                "timestamp": utc_now_iso(),
            }

        combined = {
            "listing": entry["listing"],
            "enrichment": entry.get("enrichment") or {},
            "keystone": entry.get("keystone") or {},
        }
        showcase_path = self.stage_for_showcase(combined)

        entry["queue_status"] = "APPROVED_FOR_SHOWCASE"
        entry["approved_at"] = utc_now_iso()
        entry["claims"] = dict(DEFAULT_CLAIMS)

        entries = self._load_queue()
        for idx, item in enumerate(entries):
            if item.get("listing_id") == listing_id:
                entries[idx] = entry
                break
        self._write_queue(entries)

        approved_entry = self._build_showcase_entry(combined)
        approved_entry["workflow_status"] = "APPROVED_FOR_SHOWCASE"
        approved_entry["claims"]["mls_connected"] = False
        approved_entry["claims"]["published_live"] = False

        return {
            "status": "APPROVED_FOR_SHOWCASE",
            "listing_id": listing_id,
            "showcase_path": str(showcase_path),
            "showcase_entry": approved_entry,
            "claims": dict(DEFAULT_CLAIMS),
            "external_send_blocked": True,
            "timestamp": utc_now_iso(),
        }

    def process_submission(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Full pipeline: ingest → enrich → queue (use approve_for_showcase to publish)."""
        return self.process_intake_submission(payload)
