"""
AstroCam Sync - Astronomical Target Catalog
============================================

Comprehensive catalog of deep-sky objects, planets, and other astronomical targets
with detailed observation parameters for astrophotography planning.

This module contains 50+ carefully curated astronomical targets with precise
coordinates, physical characteristics, and imaging recommendations.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Optional, Tuple
from datetime import datetime


class TargetType(Enum):
    """Classification of astronomical targets."""
    MILKY_WAY = auto()
    GALAXY = auto()
    NEBULA = auto()
    PLANETARY_NEBULA = auto()
    STAR_CLUSTER_OPEN = auto()
    STAR_CLUSTER_GLOBULAR = auto()
    PLANET = auto()
    SATELLITE = auto()
    SUPERNOVA_REMNANT = auto()
    MOLECULAR_CLOUD = auto()
    DARK_NEBULA = auto()


class Season(Enum):
    """Optimal viewing seasons."""
    WINTER = "Winter"
    SPRING = "Spring"
    SUMMER = "Summer"
    FALL = "Fall"
    YEAR_ROUND = "Year-round"


class Hemisphere(Enum):
    """Observable hemisphere."""
    NORTHERN = "Northern"
    SOUTHERN = "Southern"
    BOTH = "Both"


class Equipment(Enum):
    """Recommended equipment tier."""
    NAKED_EYE = "Naked Eye"
    BINOCULARS = "Binoculars"
    SMALL_TELESCOPE = "Small Telescope (50-80mm)"
    MEDIUM_TELESCOPE = "Medium Telescope (80-150mm)"
    LARGE_TELESCOPE = "Large Telescope (150mm+)"
    WIDE_FIELD = "Wide Field Lens (14-50mm)"
    TELEPHOTO = "Telephoto Lens (135-300mm)"
    SUPER_TELEPHOTO = "Super Telephoto (400mm+)"


class FilterRecommendation(Enum):
    """Recommended filters for imaging."""
    NONE = "No filter"
    UHC = "UHC (Ultra High Contrast)"
    OIII = "OIII (Oxygen III)"
    H_ALPHA = "H-alpha"
    SII = "SII (Sulfur II)"
    LIGHT_POLLUTION = "Light Pollution Filter"
    BROADBAND = "Broadband RGB"
    NARROWBAND = "Narrowband (Ha-OIII-SII)"
    L_RGB = "Luminance + RGB"


@dataclass
class ExposureGuideline:
    """Imaging exposure recommendations."""
    single_exposure_sec: int  # Recommended single exposure time
    total_exposure_min: int   # Recommended total integration time
    iso_gain: str             # ISO/Gain recommendation
    filters: List[FilterRecommendation] = field(default_factory=list)
    notes: str = ""


@dataclass
class Target:
    """
    Astronomical target with complete observation and imaging parameters.

    Attributes:
        name: Primary designation
        common_name: Popular name
        target_type: Classification
        ra_hours: Right Ascension in hours (J2000)
        dec_degrees: Declination in degrees (J2000)
        magnitude: Visual magnitude
        surface_brightness: mag/arcsec² (for extended objects)
        angular_size: Angular size in arcminutes (width x height)
        distance_ly: Distance in light-years
        constellation: Host constellation
        optimal_months: List of best viewing months (1-12)
        seasons: List of optimal seasons
        hemisphere: Observable hemisphere
        equipment: Recommended equipment
        exposure: Exposure guidelines
        description: Detailed description
        difficulty: Imaging difficulty (1-10, 10=hardest)
        catalog_ids: Alternative catalog designations
    """
    name: str
    common_name: str
    target_type: TargetType
    ra_hours: float
    dec_degrees: float
    magnitude: float
    surface_brightness: Optional[float]
    angular_size: Tuple[float, float]  # arcminutes (width, height)
    distance_ly: Optional[float]
    constellation: str
    optimal_months: List[int]
    seasons: List[Season]
    hemisphere: Hemisphere
    equipment: List[Equipment]
    exposure: ExposureGuideline
    description: str
    difficulty: int
    catalog_ids: List[str] = field(default_factory=list)

    def get_ra_hms(self) -> Tuple[int, int, float]:
        """Convert RA hours to hours, minutes, seconds."""
        hours = int(self.ra_hours)
        remaining = (self.ra_hours - hours) * 60
        minutes = int(remaining)
        seconds = (remaining - minutes) * 60
        return hours, minutes, seconds

    def get_dec_dms(self) -> Tuple[int, int, float]:
        """Convert Dec degrees to degrees, arcminutes, arcseconds."""
        sign = 1 if self.dec_degrees >= 0 else -1
        abs_dec = abs(self.dec_degrees)
        degrees = int(abs_dec)
        remaining = (abs_dec - degrees) * 60
        arcminutes = int(remaining)
        arcseconds = (remaining - arcminutes) * 60
        return sign * degrees, arcminutes, arcseconds

    def is_visible_tonight(self, observer_lat: float, date: datetime) -> bool:
        """
        Determine if target is optimally visible for given observer and date.

        Args:
            observer_lat: Observer's latitude in degrees
            date: Observation date

        Returns:
            True if target is in optimal viewing season
        """
        month = date.month
        return month in self.optimal_months


# ============================================================================
# MILKY WAY TARGETS
# ============================================================================

MILKY_WAY_CORE = Target(
    name="Milky Way Galactic Center",
    common_name="Milky Way Core",
    target_type=TargetType.MILKY_WAY,
    ra_hours=17.7608,
    dec_degrees=-29.0,
    magnitude=-1.0,
    surface_brightness=None,
    angular_size=(30.0, 20.0),  # degrees
    distance_ly=26000,
    constellation="Sagittarius",
    optimal_months=[5, 6, 7, 8, 9],
    seasons=[Season.SUMMER],
    hemisphere=Hemisphere.BOTH,
    equipment=[Equipment.WIDE_FIELD, Equipment.TELEPHOTO],
    exposure=ExposureGuideline(
        single_exposure_sec=120,
        total_exposure_min=60,
        iso_gain="ISO 1600-3200",
        filters=[FilterRecommendation.LIGHT_POLLUTION],
        notes="Use wide field lens, tracked or panorama. Dark skies essential."
    ),
    description="The luminous central bulge of our galaxy, rich with nebulae and star clouds. "
                "Best viewed from southern latitudes. Contains numerous dark nebulae including the Dark Horse.",
    difficulty=3,
    catalog_ids=["Sgr A*"]
)

SUMMER_TRIANGLE = Target(
    name="Summer Triangle",
    common_name="Summer Triangle Asterism",
    target_type=TargetType.MILKY_WAY,
    ra_hours=19.5,
    dec_degrees=35.0,
    magnitude=0.0,
    surface_brightness=None,
    angular_size=(60.0, 50.0),  # degrees
    distance_ly=None,
    constellation="Cygnus/Lyra/Aquila",
    optimal_months=[6, 7, 8, 9, 10],
    seasons=[Season.SUMMER, Season.FALL],
    hemisphere=Hemisphere.NORTHERN,
    equipment=[Equipment.WIDE_FIELD],
    exposure=ExposureGuideline(
        single_exposure_sec=180,
        total_exposure_min=90,
        iso_gain="ISO 1600-3200",
        filters=[FilterRecommendation.LIGHT_POLLUTION],
        notes="Ultra-wide lens (14-24mm), tracked. Captures Cygnus Rift and Great Rift."
    ),
    description="Asterism formed by Vega, Deneb, and Altair. The region contains the Cygnus Rift, "
                "a dark nebula complex visible as a dark lane splitting the Milky Way.",
    difficulty=2,
    catalog_ids=["Vega", "Deneb", "Altair"]
)


# ============================================================================
# GALAXIES
# ============================================================================

M31_ANDROMEDA = Target(
    name="M31",
    common_name="Andromeda Galaxy",
    target_type=TargetType.GALAXY,
    ra_hours=0.7125,
    dec_degrees=41.2692,
    magnitude=3.4,
    surface_brightness=13.5,
    angular_size=(178.0, 63.0),
    distance_ly=2537000,
    constellation="Andromeda",
    optimal_months=[9, 10, 11, 12, 1],
    seasons=[Season.FALL, Season.WINTER],
    hemisphere=Hemisphere.NORTHERN,
    equipment=[Equipment.WIDE_FIELD, Equipment.TELEPHOTO],
    exposure=ExposureGuideline(
        single_exposure_sec=180,
        total_exposure_min=120,
        iso_gain="ISO 800-1600",
        filters=[FilterRecommendation.BROADBAND, FilterRecommendation.LIGHT_POLLUTION],
        notes="Wide field captures M31, M32, M110. Use 135-200mm for full galaxy."
    ),
    description="Nearest major galaxy to the Milky Way and largest member of the Local Group. "
                "Visible to naked eye as fuzzy patch. Contains over 1 trillion stars.",
    difficulty=1,
    catalog_ids=["NGC 224", "Andromeda Galaxy"]
)

M33_TRIANGULUM = Target(
    name="M33",
    common_name="Triangulum Galaxy",
    target_type=TargetType.GALAXY,
    ra_hours=1.5642,
    dec_degrees=30.6600,
    magnitude=5.7,
    surface_brightness=14.2,
    angular_size=(73.0, 45.0),
    distance_ly=2730000,
    constellation="Triangulum",
    optimal_months=[10, 11, 12, 1],
    seasons=[Season.FALL, Season.WINTER],
    hemisphere=Hemisphere.NORTHERN,
    equipment=[Equipment.TELEPHOTO, Equipment.MEDIUM_TELESCOPE],
    exposure=ExposureGuideline(
        single_exposure_sec=240,
        total_exposure_min=180,
        iso_gain="ISO 800-1600",
        filters=[FilterRecommendation.BROADBAND],
        notes="Low surface brightness, requires dark skies and long exposure."
    ),
    description="Third-largest galaxy in the Local Group. Face-on spiral with prominent HII regions. "
                "Challenging due to low surface brightness despite large angular size.",
    difficulty=6,
    catalog_ids=["NGC 598", "Triangulum Galaxy"]
)

M51_WHIRLPOOL = Target(
    name="M51",
    common_name="Whirlpool Galaxy",
    target_type=TargetType.GALAXY,
    ra_hours=13.4958,
    dec_degrees=47.1953,
    magnitude=8.4,
    surface_brightness=13.0,
    angular_size=(11.2, 6.9),
    distance_ly=23000000,
    constellation="Canes Venatici",
    optimal_months=[3, 4, 5, 6],
    seasons=[Season.SPRING, Season.SUMMER],
    hemisphere=Hemisphere.NORTHERN,
    equipment=[Equipment.TELEPHOTO, Equipment.MEDIUM_TELESCOPE],
    exposure=ExposureGuideline(
        single_exposure_sec=300,
        total_exposure_min=240,
        iso_gain="ISO 800",
        filters=[FilterRecommendation.L_RGB],
        notes="Classic target showing spiral structure and companion NGC 5195."
    ),
    description="Grand design spiral galaxy interacting with companion NGC 5195. "
                "One of the most photogenic galaxies with well-defined spiral arms.",
    difficulty=4,
    catalog_ids=["NGC 5194", "Whirlpool Galaxy"]
)

M81_BODES = Target(
    name="M81",
    common_name="Bode's Galaxy",
    target_type=TargetType.GALAXY,
    ra_hours=9.9258,
    dec_degrees=69.0650,
    magnitude=6.9,
    surface_brightness=12.9,
    angular_size=(26.9, 14.1),
    distance_ly=11800000,
    constellation="Ursa Major",
    optimal_months=[2, 3, 4, 5],
    seasons=[Season.WINTER, Season.SPRING],
    hemisphere=Hemisphere.NORTHERN,
    equipment=[Equipment.TELEPHOTO, Equipment.MEDIUM_TELESCOPE],
    exposure=ExposureGuideline(
        single_exposure_sec=300,
        total_exposure_min=180,
        iso_gain="ISO 800",
        filters=[FilterRecommendation.L_RGB],
        notes="Pair with M82 in same field of view using 200-300mm focal length."
    ),
    description="Large, bright spiral galaxy with prominent grand design structure. "
                "Forms beautiful pair with M82 (Cigar Galaxy) just 38 arcmin away.",
    difficulty=3,
    catalog_ids=["NGC 3031", "Bode's Galaxy"]
)

M82_CIGAR = Target(
    name="M82",
    common_name="Cigar Galaxy",
    target_type=TargetType.GALAXY,
    ra_hours=9.9258,
    dec_degrees=69.6797,
    magnitude=8.4,
    surface_brightness=12.3,
    angular_size=(11.2, 4.3),
    distance_ly=11500000,
    constellation="Ursa Major",
    optimal_months=[2, 3, 4, 5],
    seasons=[Season.WINTER, Season.SPRING],
    hemisphere=Hemisphere.NORTHERN,
    equipment=[Equipment.TELEPHOTO, Equipment.MEDIUM_TELESCOPE],
    exposure=ExposureGuideline(
        single_exposure_sec=300,
        total_exposure_min=180,
        iso_gain="ISO 800",
        filters=[FilterRecommendation.H_ALPHA, FilterRecommendation.L_RGB],
        notes="H-alpha reveals extensive outflow filaments from starburst activity."
    ),
    description="Starburst galaxy with violent star formation, visible as edge-on cigar shape. "
                "Shows prominent hydrogen outflows in H-alpha. Interacting with M81.",
    difficulty=3,
    catalog_ids=["NGC 3034", "Cigar Galaxy"]
)

M101_PINWHEEL = Target(
    name="M101",
    common_name="Pinwheel Galaxy",
    target_type=TargetType.GALAXY,
    ra_hours=14.0542,
    dec_degrees=54.3489,
    magnitude=7.9,
    surface_brightness=14.8,
    angular_size=(28.8, 26.9),
    distance_ly=21000000,
    constellation="Ursa Major",
    optimal_months=[3, 4, 5, 6],
    seasons=[Season.SPRING, Season.SUMMER],
    hemisphere=Hemisphere.NORTHERN,
    equipment=[Equipment.TELEPHOTO, Equipment.MEDIUM_TELESCOPE],
    exposure=ExposureGuideline(
        single_exposure_sec=300,
        total_exposure_min=300,
        iso_gain="ISO 800",
        filters=[FilterRecommendation.L_RGB],
        notes="Large but low surface brightness. Requires dark skies and long integration."
    ),
    description="Face-on spiral galaxy with asymmetric arms. Large angular size but challenging "
                "due to low surface brightness. Contains over 3000 HII regions.",
    difficulty=7,
    catalog_ids=["NGC 5457", "Pinwheel Galaxy"]
)


# ============================================================================
# EMISSION NEBULAE
# ============================================================================

M42_ORION = Target(
    name="M42",
    common_name="Orion Nebula",
    target_type=TargetType.NEBULA,
    ra_hours=5.5833,
    dec_degrees=-5.3911,
    magnitude=4.0,
    surface_brightness=17.0,
    angular_size=(65.0, 60.0),
    distance_ly=1344,
    constellation="Orion",
    optimal_months=[11, 12, 1, 2, 3],
    seasons=[Season.WINTER],
    hemisphere=Hemisphere.BOTH,
    equipment=[Equipment.TELEPHOTO, Equipment.SMALL_TELESCOPE],
    exposure=ExposureGuideline(
        single_exposure_sec=30,  # Core is bright, needs HDR
        total_exposure_min=60,
        iso_gain="ISO 400-800",
        filters=[FilterRecommendation.BROADBAND, FilterRecommendation.UHC],
        notes="HDR required: short exposures for core, long for outer nebulosity."
    ),
    description="Brightest nebula in the sky, visible to naked eye. Stellar nursery with the "
                "Trapezium cluster at its heart. Nearest massive star-forming region.",
    difficulty=2,
    catalog_ids=["NGC 1976", "Orion Nebula"]
)

M8_LAGOON = Target(
    name="M8",
    common_name="Lagoon Nebula",
    target_type=TargetType.NEBULA,
    ra_hours=18.0650,
    dec_degrees=-24.3833,
    magnitude=6.0,
    surface_brightness=13.0,
    angular_size=(90.0, 40.0),
    distance_ly=4100,
    constellation="Sagittarius",
    optimal_months=[6, 7, 8],
    seasons=[Season.SUMMER],
    hemisphere=Hemisphere.BOTH,
    equipment=[Equipment.TELEPHOTO, Equipment.SMALL_TELESCOPE],
    exposure=ExposureGuideline(
        single_exposure_sec=180,
        total_exposure_min=120,
        iso_gain="ISO 800-1600",
        filters=[FilterRecommendation.NARROWBAND, FilterRecommendation.H_ALPHA],
        notes="Narrowband imaging reveals intricate structure and dark lanes."
    ),
    description="Large, bright emission nebula with embedded open cluster NGC 6530. "
                "Features prominent dark dust lane bisecting the nebula.",
    difficulty=3,
    catalog_ids=["NGC 6523", "Lagoon Nebula"]
)

M16_EAGLE = Target(
    name="M16",
    common_name="Eagle Nebula",
    target_type=TargetType.NEBULA,
    ra_hours=18.3156,
    dec_degrees=-13.7833,
    magnitude=6.4,
    surface_brightness=12.0,
    angular_size=(30.0, 28.0),
    distance_ly=7000,
    constellation="Serpens",
    optimal_months=[6, 7, 8],
    seasons=[Season.SUMMER],
    hemisphere=Hemisphere.BOTH,
    equipment=[Equipment.TELEPHOTO, Equipment.MEDIUM_TELESCOPE],
    exposure=ExposureGuideline(
        single_exposure_sec=300,
        total_exposure_min=240,
        iso_gain="ISO 800-1600",
        filters=[FilterRecommendation.NARROWBAND, FilterRecommendation.H_ALPHA],
        notes="Long focal length needed to resolve Pillars of Creation detail."
    ),
    description="Star-forming nebula famous for the 'Pillars of Creation' imaged by Hubble. "
                "Contains active star formation and an embedded young star cluster.",
    difficulty=5,
    catalog_ids=["NGC 6611", "Eagle Nebula", "Pillars of Creation"]
)

M17_OMEGA = Target(
    name="M17",
    common_name="Omega Nebula",
    target_type=TargetType.NEBULA,
    ra_hours=18.3408,
    dec_degrees=-16.1833,
    magnitude=6.0,
    surface_brightness=12.0,
    angular_size=(46.0, 37.0),
    distance_ly=5500,
    constellation="Sagittarius",
    optimal_months=[6, 7, 8],
    seasons=[Season.SUMMER],
    hemisphere=Hemisphere.BOTH,
    equipment=[Equipment.TELEPHOTO, Equipment.MEDIUM_TELESCOPE],
    exposure=ExposureGuideline(
        single_exposure_sec=240,
        total_exposure_min=180,
        iso_gain="ISO 800-1600",
        filters=[FilterRecommendation.NARROWBAND],
        notes="Narrowband palette reveals swan-like structure in great detail."
    ),
    description="Also known as Swan, Horseshoe, or Lobster Nebula. One of the youngest and "
                "most massive star-forming regions known, with over 800 solar masses.",
    difficulty=4,
    catalog_ids=["NGC 6618", "Omega Nebula", "Swan Nebula"]
)

M20_TRIFID = Target(
    name="M20",
    common_name="Trifid Nebula",
    target_type=TargetType.NEBULA,
    ra_hours=18.0333,
    dec_degrees=-23.0333,
    magnitude=6.3,
    surface_brightness=11.5,
    angular_size=(28.0, 28.0),
    distance_ly=5200,
    constellation="Sagittarius",
    optimal_months=[6, 7, 8],
    seasons=[Season.SUMMER],
    hemisphere=Hemisphere.BOTH,
    equipment=[Equipment.TELEPHOTO, Equipment.MEDIUM_TELESCOPE],
    exposure=ExposureGuideline(
        single_exposure_sec=300,
        total_exposure_min=180,
        iso_gain="ISO 800-1600",
        filters=[FilterRecommendation.NARROWBAND, FilterRecommendation.L_RGB],
        notes="Combination of emission (red) and reflection (blue) nebulae."
    ),
    description="Unique nebula with both emission and reflection components. Named for three "
                "dark dust lanes dividing the emission nebula. Often paired with M8.",
    difficulty=4,
    catalog_ids=["NGC 6514", "Trifid Nebula"]
)

HORSEHEAD_NEBULA = Target(
    name="IC 434",
    common_name="Horsehead Nebula",
    target_type=TargetType.DARK_NEBULA,
    ra_hours=5.6833,
    dec_degrees=-2.4500,
    magnitude=None,
    surface_brightness=None,
    angular_size=(8.0, 6.0),
    distance_ly=1500,
    constellation="Orion",
    optimal_months=[11, 12, 1, 2],
    seasons=[Season.WINTER],
    hemisphere=Hemisphere.BOTH,
    equipment=[Equipment.TELEPHOTO, Equipment.MEDIUM_TELESCOPE],
    exposure=ExposureGuideline(
        single_exposure_sec=300,
        total_exposure_min=240,
        iso_gain="ISO 800-1600",
        filters=[FilterRecommendation.H_ALPHA],
        notes="H-alpha essential for revealing the dark nebula against emission background."
    ),
    description="Dark nebula silhouetted against emission nebula IC 434. Part of the Orion "
                "Molecular Cloud Complex. One of the most recognizable features in astronomy.",
    difficulty=7,
    catalog_ids=["Barnard 33", "Horsehead Nebula"]
)

CALIFORNIA_NEBULA = Target(
    name="NGC 1499",
    common_name="California Nebula",
    target_type=TargetType.NEBULA,
    ra_hours=4.0500,
    dec_degrees=36.4167,
    magnitude=5.0,
    surface_brightness=20.0,
    angular_size=(160.0, 40.0),
    distance_ly=1000,
    constellation="Perseus",
    optimal_months=[10, 11, 12, 1],
    seasons=[Season.FALL, Season.WINTER],
    hemisphere=Hemisphere.NORTHERN,
    equipment=[Equipment.WIDE_FIELD, Equipment.TELEPHOTO],
    exposure=ExposureGuideline(
        single_exposure_sec=300,
        total_exposure_min=240,
        iso_gain="ISO 1600-3200",
        filters=[FilterRecommendation.H_ALPHA],
        notes="Very faint without H-alpha filter. Wide field essential for full extent."
    ),
    description="Extremely faint emission nebula spanning 2.5 degrees, resembling California. "
                "Illuminated by the bright star Xi Persei. Invisible without narrowband filters.",
    difficulty=8,
    catalog_ids=["NGC 1499", "California Nebula"]
)

NORTH_AMERICA_NEBULA = Target(
    name="NGC 7000",
    common_name="North America Nebula",
    target_type=TargetType.NEBULA,
    ra_hours=20.9667,
    dec_degrees=44.3333,
    magnitude=4.0,
    surface_brightness=22.0,
    angular_size=(120.0, 100.0),
    distance_ly=2200,
    constellation="Cygnus",
    optimal_months=[7, 8, 9, 10],
    seasons=[Season.SUMMER, Season.FALL],
    hemisphere=Hemisphere.NORTHERN,
    equipment=[Equipment.WIDE_FIELD, Equipment.TELEPHOTO],
    exposure=ExposureGuideline(
        single_exposure_sec=240,
        total_exposure_min=180,
        iso_gain="ISO 1600-3200",
        filters=[FilterRecommendation.H_ALPHA, FilterRecommendation.UHC],
        notes="Wide field captures North America and Pelican nebulae together."
    ),
    description="Large emission nebula resembling the North American continent. "
                "The 'Gulf of Mexico' is actually a dark nebula. Adjacent to Pelican Nebula.",
    difficulty=5,
    catalog_ids=["NGC 7000", "North America Nebula"]
)

VEIL_NEBULA = Target(
    name="NGC 6960/6992",
    common_name="Veil Nebula Complex",
    target_type=TargetType.SUPERNOVA_REMNANT,
    ra_hours=20.7583,
    dec_degrees=30.7167,
    magnitude=7.0,
    surface_brightness=15.0,
    angular_size=(180.0, 180.0),
    distance_ly=2400,
    constellation="Cygnus",
    optimal_months=[7, 8, 9, 10],
    seasons=[Season.SUMMER, Season.FALL],
    hemisphere=Hemisphere.NORTHERN,
    equipment=[Equipment.TELEPHOTO, Equipment.MEDIUM_TELESCOPE],
    exposure=ExposureGuideline(
        single_exposure_sec=300,
        total_exposure_min=300,
        iso_gain="ISO 800-1600",
        filters=[FilterRecommendation.OIII, FilterRecommendation.H_ALPHA],
        notes="OIII brings out structure. Mosaic needed for full complex."
    ),
    description="Supernova remnant from explosion 8000 years ago. Expanding shell of ionized gas. "
                "Western Veil (NGC 6960) and Eastern Veil (NGC 6992) are main components.",
    difficulty=6,
    catalog_ids=["NGC 6960", "NGC 6992", "Veil Nebula", "Cygnus Loop"]
)

ROSETTE_NEBULA = Target(
    name="NGC 2237",
    common_name="Rosette Nebula",
    target_type=TargetType.NEBULA,
    ra_hours=6.5333,
    dec_degrees=4.9500,
    magnitude=9.0,
    surface_brightness=13.0,
    angular_size=(80.0, 60.0),
    distance_ly=5200,
    constellation="Monoceros",
    optimal_months=[12, 1, 2, 3],
    seasons=[Season.WINTER],
    hemisphere=Hemisphere.BOTH,
    equipment=[Equipment.TELEPHOTO, Equipment.MEDIUM_TELESCOPE],
    exposure=ExposureGuideline(
        single_exposure_sec=300,
        total_exposure_min=240,
        iso_gain="ISO 800-1600",
        filters=[FilterRecommendation.NARROWBAND, FilterRecommendation.H_ALPHA],
        notes="Narrowband reveals intricate petal-like structure around central cavity."
    ),
    description="Large, circular emission nebula with open cluster NGC 2244 at center. "
                "Stellar winds from cluster have cleared the central cavity.",
    difficulty=5,
    catalog_ids=["NGC 2237", "NGC 2244", "Rosette Nebula"]
)

CARINA_NEBULA = Target(
    name="NGC 3372",
    common_name="Carina Nebula",
    target_type=TargetType.NEBULA,
    ra_hours=10.7333,
    dec_degrees=-59.8667,
    magnitude=3.0,
    surface_brightness=10.0,
    angular_size=(120.0, 120.0),
    distance_ly=7500,
    constellation="Carina",
    optimal_months=[2, 3, 4, 5],
    seasons=[Season.SUMMER],  # Southern hemisphere summer
    hemisphere=Hemisphere.SOUTHERN,
    equipment=[Equipment.TELEPHOTO, Equipment.MEDIUM_TELESCOPE],
    exposure=ExposureGuideline(
        single_exposure_sec=180,
        total_exposure_min=180,
        iso_gain="ISO 800-1600",
        filters=[FilterRecommendation.NARROWBAND, FilterRecommendation.L_RGB],
        notes="One of the largest nebulae. Contains Eta Carinae and Keyhole Nebula."
    ),
    description="Massive star-forming nebula, four times larger than Orion. Contains the "
                "hypergiant star Eta Carinae and the famous Mystic Mountain pillars.",
    difficulty=3,
    catalog_ids=["NGC 3372", "Carina Nebula", "Eta Carinae"]
)


# ============================================================================
# STAR CLUSTERS
# ============================================================================

M45_PLEIADES = Target(
    name="M45",
    common_name="Pleiades",
    target_type=TargetType.STAR_CLUSTER_OPEN,
    ra_hours=3.7833,
    dec_degrees=24.1167,
    magnitude=1.6,
    surface_brightness=None,
    angular_size=(110.0, 110.0),
    distance_ly=444,
    constellation="Taurus",
    optimal_months=[11, 12, 1, 2],
    seasons=[Season.FALL, Season.WINTER],
    hemisphere=Hemisphere.NORTHERN,
    equipment=[Equipment.WIDE_FIELD, Equipment.TELEPHOTO],
    exposure=ExposureGuideline(
        single_exposure_sec=120,
        total_exposure_min=90,
        iso_gain="ISO 800-1600",
        filters=[FilterRecommendation.BROADBAND],
        notes="Medium focal length reveals reflection nebulosity around stars."
    ),
    description="Bright open cluster of young stars with blue reflection nebulosity. "
                "Seven sisters visible to naked eye, over 1000 stars total in cluster.",
    difficulty=1,
    catalog_ids=["Seven Sisters", "Pleiades"]
)

M13_HERCULES = Target(
    name="M13",
    common_name="Hercules Globular Cluster",
    target_type=TargetType.STAR_CLUSTER_GLOBULAR,
    ra_hours=16.6950,
    dec_degrees=36.4617,
    magnitude=5.8,
    surface_brightness=11.0,
    angular_size=(20.0, 20.0),
    distance_ly=25100,
    constellation="Hercules",
    optimal_months=[5, 6, 7, 8],
    seasons=[Season.SPRING, Season.SUMMER],
    hemisphere=Hemisphere.NORTHERN,
    equipment=[Equipment.TELEPHOTO, Equipment.MEDIUM_TELESCOPE],
    exposure=ExposureGuideline(
        single_exposure_sec=180,
        total_exposure_min=120,
        iso_gain="ISO 800",
        filters=[FilterRecommendation.BROADBAND],
        notes="Moderate focal length. Core resolves with good seeing."
    ),
    description="Brightest globular cluster in northern hemisphere. Contains over 300,000 stars. "
                "Famous for 1974 Arecibo message sent toward it.",
    difficulty=2,
    catalog_ids=["NGC 6205", "Great Hercules Cluster"]
)

OMEGA_CENTAURI = Target(
    name="NGC 5139",
    common_name="Omega Centauri",
    target_type=TargetType.STAR_CLUSTER_GLOBULAR,
    ra_hours=13.4433,
    dec_degrees=-47.4789,
    magnitude=3.9,
    surface_brightness=7.9,
    angular_size=(36.3, 36.3),
    distance_ly=15800,
    constellation="Centaurus",
    optimal_months=[3, 4, 5, 6],
    seasons=[Season.FALL],  # Southern hemisphere
    hemisphere=Hemisphere.SOUTHERN,
    equipment=[Equipment.TELEPHOTO, Equipment.MEDIUM_TELESCOPE],
    exposure=ExposureGuideline(
        single_exposure_sec=120,
        total_exposure_min=90,
        iso_gain="ISO 800",
        filters=[FilterRecommendation.BROADBAND],
        notes="Largest globular cluster. Visible to naked eye as fuzzy star."
    ),
    description="Largest and brightest globular cluster in Milky Way. Contains ~10 million stars. "
                "Likely the core of a dwarf galaxy absorbed by the Milky Way.",
    difficulty=1,
    catalog_ids=["NGC 5139", "Omega Centauri"]
)

CLUSTER_47_TUC = Target(
    name="NGC 104",
    common_name="47 Tucanae",
    target_type=TargetType.STAR_CLUSTER_GLOBULAR,
    ra_hours=0.4033,
    dec_degrees=-72.0814,
    magnitude=4.0,
    surface_brightness=8.2,
    angular_size=(30.9, 30.9),
    distance_ly=16700,
    constellation="Tucana",
    optimal_months=[9, 10, 11, 12],
    seasons=[Season.SPRING],  # Southern hemisphere
    hemisphere=Hemisphere.SOUTHERN,
    equipment=[Equipment.TELEPHOTO, Equipment.MEDIUM_TELESCOPE],
    exposure=ExposureGuideline(
        single_exposure_sec=120,
        total_exposure_min=90,
        iso_gain="ISO 800",
        filters=[FilterRecommendation.BROADBAND],
        notes="Second brightest globular after Omega Centauri."
    ),
    description="Second most spectacular globular cluster, visible to naked eye. Dense core with "
                "millions of stars. Contains over 23 millisecond pulsars.",
    difficulty=1,
    catalog_ids=["NGC 104", "47 Tucanae"]
)

DOUBLE_CLUSTER = Target(
    name="NGC 869/884",
    common_name="Double Cluster",
    target_type=TargetType.STAR_CLUSTER_OPEN,
    ra_hours=2.3333,
    dec_degrees=57.1333,
    magnitude=4.3,
    surface_brightness=None,
    angular_size=(60.0, 60.0),
    distance_ly=7500,
    constellation="Perseus",
    optimal_months=[10, 11, 12, 1],
    seasons=[Season.FALL, Season.WINTER],
    hemisphere=Hemisphere.NORTHERN,
    equipment=[Equipment.BINOCULARS, Equipment.WIDE_FIELD, Equipment.SMALL_TELESCOPE],
    exposure=ExposureGuideline(
        single_exposure_sec=120,
        total_exposure_min=60,
        iso_gain="ISO 800-1600",
        filters=[FilterRecommendation.BROADBAND],
        notes="Wide field essential to capture both clusters. Beautiful in binoculars."
    ),
    description="Pair of open clusters visible to naked eye as fuzzy patch. Each contains "
                "300+ stars. Relatively young at 12.8 million years old.",
    difficulty=1,
    catalog_ids=["NGC 869", "NGC 884", "h and χ Persei"]
)


# ============================================================================
# PLANETS
# ============================================================================

MOON = Target(
    name="Moon",
    common_name="Earth's Moon",
    target_type=TargetType.SATELLITE,
    ra_hours=0.0,  # Variable
    dec_degrees=0.0,  # Variable
    magnitude=-12.74,
    surface_brightness=None,
    angular_size=(31.0, 31.0),  # arcminutes
    distance_ly=None,
    constellation="Variable",
    optimal_months=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
    seasons=[Season.YEAR_ROUND],
    hemisphere=Hemisphere.BOTH,
    equipment=[Equipment.TELEPHOTO, Equipment.SUPER_TELEPHOTO],
    exposure=ExposureGuideline(
        single_exposure_sec=1,  # Very short, use 1/125 - 1/500 sec
        total_exposure_min=5,
        iso_gain="ISO 100-400",
        filters=[FilterRecommendation.NONE],
        notes="Fast shutter speeds. Lunar imaging benefits from stacking many frames."
    ),
    description="Earth's only natural satellite. Ideal target for planetary imaging techniques. "
                "Best results along terminator during partial phases.",
    difficulty=1,
    catalog_ids=["Luna"]
)

JUPITER = Target(
    name="Jupiter",
    common_name="Jupiter",
    target_type=TargetType.PLANET,
    ra_hours=0.0,  # Variable
    dec_degrees=0.0,  # Variable
    magnitude=-2.94,
    surface_brightness=None,
    angular_size=(0.82, 0.77),  # arcminutes at opposition
    distance_ly=None,
    constellation="Variable",
    optimal_months=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
    seasons=[Season.YEAR_ROUND],
    hemisphere=Hemisphere.BOTH,
    equipment=[Equipment.SUPER_TELEPHOTO, Equipment.LARGE_TELESCOPE],
    exposure=ExposureGuideline(
        single_exposure_sec=1,  # Use high FPS video
        total_exposure_min=10,
        iso_gain="ISO 400-800",
        filters=[FilterRecommendation.NONE],
        notes="Video capture with ADC. Stack thousands of frames. Image at opposition."
    ),
    description="Largest planet in solar system. Shows cloud bands, Great Red Spot, and "
                "Galilean moons. Rotates in under 10 hours.",
    difficulty=4,
    catalog_ids=["Sol V"]
)

SATURN = Target(
    name="Saturn",
    common_name="Saturn",
    target_type=TargetType.PLANET,
    ra_hours=0.0,  # Variable
    dec_degrees=0.0,  # Variable
    magnitude=0.46,
    surface_brightness=None,
    angular_size=(0.33, 0.30),  # arcminutes at opposition (excluding rings)
    distance_ly=None,
    constellation="Variable",
    optimal_months=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
    seasons=[Season.YEAR_ROUND],
    hemisphere=Hemisphere.BOTH,
    equipment=[Equipment.SUPER_TELEPHOTO, Equipment.LARGE_TELESCOPE],
    exposure=ExposureGuideline(
        single_exposure_sec=1,  # Use high FPS video
        total_exposure_min=10,
        iso_gain="ISO 400-800",
        filters=[FilterRecommendation.NONE],
        notes="Requires steady seeing. ADC beneficial. Ring angle varies with Saturn's season."
    ),
    description="Ringed gas giant with spectacular ring system. Cassini Division visible in "
                "good seeing. Titan and other moons observable.",
    difficulty=5,
    catalog_ids=["Sol VI"]
)

MARS = Target(
    name="Mars",
    common_name="Mars",
    target_type=TargetType.PLANET,
    ra_hours=0.0,  # Variable
    dec_degrees=0.0,  # Variable
    magnitude=-2.91,
    surface_brightness=None,
    angular_size=(0.42, 0.42),  # arcminutes at opposition
    distance_ly=None,
    constellation="Variable",
    optimal_months=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
    seasons=[Season.YEAR_ROUND],
    hemisphere=Hemisphere.BOTH,
    equipment=[Equipment.SUPER_TELEPHOTO, Equipment.LARGE_TELESCOPE],
    exposure=ExposureGuideline(
        single_exposure_sec=1,  # Use high FPS video
        total_exposure_min=10,
        iso_gain="ISO 400-800",
        filters=[FilterRecommendation.NONE],
        notes="Only worthwhile at opposition. Very small angular size. RGB filters enhance detail."
    ),
    description="Red planet with polar caps and surface features visible. Best every 2.1 years "
                "at opposition when closest to Earth.",
    difficulty=6,
    catalog_ids=["Sol IV"]
)

VENUS = Target(
    name="Venus",
    common_name="Venus",
    target_type=TargetType.PLANET,
    ra_hours=0.0,  # Variable
    dec_degrees=0.0,  # Variable
    magnitude=-4.89,
    surface_brightness=None,
    angular_size=(1.0, 1.0),  # arcminutes at greatest elongation
    distance_ly=None,
    constellation="Variable",
    optimal_months=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
    seasons=[Season.YEAR_ROUND],
    hemisphere=Hemisphere.BOTH,
    equipment=[Equipment.TELEPHOTO, Equipment.MEDIUM_TELESCOPE],
    exposure=ExposureGuideline(
        single_exposure_sec=1,  # Very short exposure
        total_exposure_min=5,
        iso_gain="ISO 100-400",
        filters=[FilterRecommendation.NONE],
        notes="Best at greatest elongation. Shows phases. UV filter reveals cloud structure."
    ),
    description="Brightest planet, shows phases like Moon. Thick atmosphere prevents surface "
                "observation. Best viewed as morning/evening star.",
    difficulty=3,
    catalog_ids=["Sol II"]
)

MERCURY = Target(
    name="Mercury",
    common_name="Mercury",
    target_type=TargetType.PLANET,
    ra_hours=0.0,  # Variable
    dec_degrees=0.0,  # Variable
    magnitude=-2.48,
    surface_brightness=None,
    angular_size=(0.17, 0.17),  # arcminutes
    distance_ly=None,
    constellation="Variable",
    optimal_months=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
    seasons=[Season.YEAR_ROUND],
    hemisphere=Hemisphere.BOTH,
    equipment=[Equipment.TELEPHOTO, Equipment.MEDIUM_TELESCOPE],
    exposure=ExposureGuideline(
        single_exposure_sec=1,
        total_exposure_min=5,
        iso_gain="ISO 100-400",
        filters=[FilterRecommendation.NONE],
        notes="Observe at greatest elongation. Very close to Sun - caution required."
    ),
    description="Innermost planet, challenging to observe due to proximity to Sun. "
                "Shows phases. Best viewed at twilight during greatest elongation.",
    difficulty=8,
    catalog_ids=["Sol I"]
)

URANUS = Target(
    name="Uranus",
    common_name="Uranus",
    target_type=TargetType.PLANET,
    ra_hours=0.0,  # Variable
    dec_degrees=0.0,  # Variable
    magnitude=5.68,
    surface_brightness=None,
    angular_size=(0.06, 0.06),  # arcminutes
    distance_ly=None,
    constellation="Variable",
    optimal_months=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
    seasons=[Season.YEAR_ROUND],
    hemisphere=Hemisphere.BOTH,
    equipment=[Equipment.LARGE_TELESCOPE],
    exposure=ExposureGuideline(
        single_exposure_sec=1,
        total_exposure_min=10,
        iso_gain="ISO 800",
        filters=[FilterRecommendation.NONE],
        notes="Small disk, appears blue-green. Moons visible with large aperture."
    ),
    description="Ice giant with extreme axial tilt. Faint blue-green disk visible in telescopes. "
                "Five major moons observable with larger instruments.",
    difficulty=7,
    catalog_ids=["Sol VII"]
)

NEPTUNE = Target(
    name="Neptune",
    common_name="Neptune",
    target_type=TargetType.PLANET,
    ra_hours=0.0,  # Variable
    dec_degrees=0.0,  # Variable
    magnitude=7.78,
    surface_brightness=None,
    angular_size=(0.04, 0.04),  # arcminutes
    distance_ly=None,
    constellation="Variable",
    optimal_months=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
    seasons=[Season.YEAR_ROUND],
    hemisphere=Hemisphere.BOTH,
    equipment=[Equipment.LARGE_TELESCOPE],
    exposure=ExposureGuideline(
        single_exposure_sec=1,
        total_exposure_min=10,
        iso_gain="ISO 800-1600",
        filters=[FilterRecommendation.NONE],
        notes="Very small disk. Requires precise finder charts and good seeing."
    ),
    description="Outermost ice giant. Deep blue color, tiny disk challenging to resolve. "
                "Triton (largest moon) visible with large apertures.",
    difficulty=9,
    catalog_ids=["Sol VIII"]
)


# ============================================================================
# ADDITIONAL GALAXIES
# ============================================================================

M63_SUNFLOWER = Target(
    name="M63",
    common_name="Sunflower Galaxy",
    target_type=TargetType.GALAXY,
    ra_hours=13.2617,
    dec_degrees=42.0292,
    magnitude=9.3,
    surface_brightness=13.6,
    angular_size=(12.6, 7.2),
    distance_ly=37000000,
    constellation="Canes Venatici",
    optimal_months=[3, 4, 5, 6],
    seasons=[Season.SPRING, Season.SUMMER],
    hemisphere=Hemisphere.NORTHERN,
    equipment=[Equipment.TELEPHOTO, Equipment.MEDIUM_TELESCOPE],
    exposure=ExposureGuideline(
        single_exposure_sec=300,
        total_exposure_min=180,
        iso_gain="ISO 800",
        filters=[FilterRecommendation.L_RGB],
        notes="Flocculent spiral with many short arm segments."
    ),
    description="Bright spiral galaxy with numerous fragmented spiral arms giving sunflower "
                "appearance. Member of M51 Group.",
    difficulty=4,
    catalog_ids=["NGC 5055", "Sunflower Galaxy"]
)

M64_BLACK_EYE = Target(
    name="M64",
    common_name="Black Eye Galaxy",
    target_type=TargetType.GALAXY,
    ra_hours=12.9400,
    dec_degrees=21.6833,
    magnitude=9.4,
    surface_brightness=12.7,
    angular_size=(10.3, 5.4),
    distance_ly=24000000,
    constellation="Coma Berenices",
    optimal_months=[3, 4, 5, 6],
    seasons=[Season.SPRING, Season.SUMMER],
    hemisphere=Hemisphere.NORTHERN,
    equipment=[Equipment.TELEPHOTO, Equipment.MEDIUM_TELESCOPE],
    exposure=ExposureGuideline(
        single_exposure_sec=300,
        total_exposure_min=180,
        iso_gain="ISO 800",
        filters=[FilterRecommendation.L_RGB],
        notes="Prominent dark dust lane creates 'black eye' appearance."
    ),
    description="Spiral galaxy with spectacular dark dust band near nucleus. Counter-rotating "
                "gas in outer regions suggests past merger or accretion event.",
    difficulty=4,
    catalog_ids=["NGC 4826", "Black Eye Galaxy", "Sleeping Beauty Galaxy"]
)

M83_SOUTHERN_PINWHEEL = Target(
    name="M83",
    common_name="Southern Pinwheel Galaxy",
    target_type=TargetType.GALAXY,
    ra_hours=13.6183,
    dec_degrees=-29.8650,
    magnitude=7.5,
    surface_brightness=12.9,
    angular_size=(12.9, 11.5),
    distance_ly=15000000,
    constellation="Hydra",
    optimal_months=[3, 4, 5],
    seasons=[Season.SPRING],
    hemisphere=Hemisphere.BOTH,
    equipment=[Equipment.TELEPHOTO, Equipment.MEDIUM_TELESCOPE],
    exposure=ExposureGuideline(
        single_exposure_sec=300,
        total_exposure_min=240,
        iso_gain="ISO 800",
        filters=[FilterRecommendation.L_RGB],
        notes="Beautiful face-on spiral with prominent HII regions."
    ),
    description="Barred spiral galaxy, one of the nearest and brightest. Shows spectacular "
                "spiral structure. Has produced six supernovae in past century.",
    difficulty=3,
    catalog_ids=["NGC 5236", "Southern Pinwheel Galaxy"]
)

M87_VIRGO_A = Target(
    name="M87",
    common_name="Virgo A",
    target_type=TargetType.GALAXY,
    ra_hours=12.5133,
    dec_degrees=12.3917,
    magnitude=9.6,
    surface_brightness=13.2,
    angular_size=(8.3, 6.6),
    distance_ly=53500000,
    constellation="Virgo",
    optimal_months=[3, 4, 5, 6],
    seasons=[Season.SPRING, Season.SUMMER],
    hemisphere=Hemisphere.NORTHERN,
    equipment=[Equipment.MEDIUM_TELESCOPE, Equipment.LARGE_TELESCOPE],
    exposure=ExposureGuideline(
        single_exposure_sec=300,
        total_exposure_min=240,
        iso_gain="ISO 800",
        filters=[FilterRecommendation.L_RGB],
        notes="Contains supermassive black hole imaged by Event Horizon Telescope."
    ),
    description="Supergiant elliptical galaxy at center of Virgo Cluster. Contains 6.5 billion "
                "solar mass black hole. Powerful jet extends 5000 light-years.",
    difficulty=5,
    catalog_ids=["NGC 4486", "Virgo A"]
)

M104_SOMBRERO = Target(
    name="M104",
    common_name="Sombrero Galaxy",
    target_type=TargetType.GALAXY,
    ra_hours=12.6650,
    dec_degrees=-11.6233,
    magnitude=8.0,
    surface_brightness=11.6,
    angular_size=(8.7, 3.5),
    distance_ly=29350000,
    constellation="Virgo",
    optimal_months=[3, 4, 5, 6],
    seasons=[Season.SPRING, Season.SUMMER],
    hemisphere=Hemisphere.BOTH,
    equipment=[Equipment.TELEPHOTO, Equipment.MEDIUM_TELESCOPE],
    exposure=ExposureGuideline(
        single_exposure_sec=300,
        total_exposure_min=180,
        iso_gain="ISO 800",
        filters=[FilterRecommendation.L_RGB],
        notes="Edge-on view shows prominent dust lane and bright bulge."
    ),
    description="Edge-on spiral or lenticular galaxy with bright nucleus and prominent dust lane "
                "creating sombrero hat appearance. Contains 2000 globular clusters.",
    difficulty=3,
    catalog_ids=["NGC 4594", "Sombrero Galaxy"]
)

NGC_253_SCULPTOR = Target(
    name="NGC 253",
    common_name="Sculptor Galaxy",
    target_type=TargetType.GALAXY,
    ra_hours=0.7900,
    dec_degrees=-25.2883,
    magnitude=7.6,
    surface_brightness=13.0,
    angular_size=(27.5, 6.8),
    distance_ly=11400000,
    constellation="Sculptor",
    optimal_months=[9, 10, 11, 12],
    seasons=[Season.SPRING],  # Southern hemisphere
    hemisphere=Hemisphere.SOUTHERN,
    equipment=[Equipment.TELEPHOTO, Equipment.MEDIUM_TELESCOPE],
    exposure=ExposureGuideline(
        single_exposure_sec=300,
        total_exposure_min=180,
        iso_gain="ISO 800-1600",
        filters=[FilterRecommendation.L_RGB],
        notes="Starburst galaxy with extensive dust lanes visible."
    ),
    description="Brightest member of Sculptor Group. Intermediate spiral undergoing intense "
                "starburst phase. Dust lanes and HII regions prominent.",
    difficulty=4,
    catalog_ids=["NGC 253", "Sculptor Galaxy", "Silver Coin Galaxy"]
)


# ============================================================================
# PLANETARY NEBULAE
# ============================================================================

M27_DUMBBELL = Target(
    name="M27",
    common_name="Dumbbell Nebula",
    target_type=TargetType.PLANETARY_NEBULA,
    ra_hours=19.9933,
    dec_degrees=22.7217,
    magnitude=7.5,
    surface_brightness=11.0,
    angular_size=(8.0, 5.7),
    distance_ly=1360,
    constellation="Vulpecula",
    optimal_months=[7, 8, 9, 10],
    seasons=[Season.SUMMER, Season.FALL],
    hemisphere=Hemisphere.NORTHERN,
    equipment=[Equipment.TELEPHOTO, Equipment.MEDIUM_TELESCOPE],
    exposure=ExposureGuideline(
        single_exposure_sec=240,
        total_exposure_min=120,
        iso_gain="ISO 800",
        filters=[FilterRecommendation.OIII, FilterRecommendation.H_ALPHA],
        notes="OIII reveals outer halo. One of largest planetary nebulae."
    ),
    description="Large, bright planetary nebula. First planetary nebula discovered. "
                "Dumbbell or apple core shape. Central white dwarf is 13.5 magnitude.",
    difficulty=2,
    catalog_ids=["NGC 6853", "Dumbbell Nebula"]
)

M57_RING = Target(
    name="M57",
    common_name="Ring Nebula",
    target_type=TargetType.PLANETARY_NEBULA,
    ra_hours=18.8933,
    dec_degrees=33.0292,
    magnitude=8.8,
    surface_brightness=9.7,
    angular_size=(1.4, 1.0),
    distance_ly=2300,
    constellation="Lyra",
    optimal_months=[6, 7, 8, 9],
    seasons=[Season.SUMMER, Season.FALL],
    hemisphere=Hemisphere.NORTHERN,
    equipment=[Equipment.MEDIUM_TELESCOPE, Equipment.LARGE_TELESCOPE],
    exposure=ExposureGuideline(
        single_exposure_sec=240,
        total_exposure_min=120,
        iso_gain="ISO 800",
        filters=[FilterRecommendation.OIII],
        notes="OIII essential for outer structure. High magnification for detail."
    ),
    description="Famous planetary nebula appearing as smoke ring. Expanding shell of gas ejected "
                "by dying star. Central white dwarf visible with large telescopes.",
    difficulty=3,
    catalog_ids=["NGC 6720", "Ring Nebula"]
)

NGC_7293_HELIX = Target(
    name="NGC 7293",
    common_name="Helix Nebula",
    target_type=TargetType.PLANETARY_NEBULA,
    ra_hours=22.4933,
    dec_degrees=-20.8378,
    magnitude=7.6,
    surface_brightness=13.5,
    angular_size=(28.0, 23.0),
    distance_ly=655,
    constellation="Aquarius",
    optimal_months=[8, 9, 10, 11],
    seasons=[Season.SUMMER, Season.FALL],
    hemisphere=Hemisphere.BOTH,
    equipment=[Equipment.TELEPHOTO, Equipment.MEDIUM_TELESCOPE],
    exposure=ExposureGuideline(
        single_exposure_sec=300,
        total_exposure_min=240,
        iso_gain="ISO 1600-3200",
        filters=[FilterRecommendation.OIII, FilterRecommendation.H_ALPHA],
        notes="Large but low surface brightness. Narrowband essential. Wide field."
    ),
    description="Nearest planetary nebula to Earth, nicknamed 'Eye of God'. Large angular size "
                "but challenging due to low surface brightness. HST revealed cometary knots.",
    difficulty=6,
    catalog_ids=["NGC 7293", "Helix Nebula", "Eye of God"]
)

NGC_7635_BUBBLE = Target(
    name="NGC 7635",
    common_name="Bubble Nebula",
    target_type=TargetType.NEBULA,
    ra_hours=23.3400,
    dec_degrees=61.2000,
    magnitude=11.0,
    surface_brightness=11.0,
    angular_size=(15.0, 8.0),
    distance_ly=7100,
    constellation="Cassiopeia",
    optimal_months=[9, 10, 11, 12, 1],
    seasons=[Season.FALL, Season.WINTER],
    hemisphere=Hemisphere.NORTHERN,
    equipment=[Equipment.TELEPHOTO, Equipment.MEDIUM_TELESCOPE],
    exposure=ExposureGuideline(
        single_exposure_sec=300,
        total_exposure_min=240,
        iso_gain="ISO 800-1600",
        filters=[FilterRecommendation.NARROWBAND, FilterRecommendation.H_ALPHA],
        notes="Often imaged with M52 cluster. Narrowband reveals shell structure."
    ),
    description="Emission nebula blown by stellar wind from massive Wolf-Rayet star. "
                "Bubble shape created by stellar wind pushing against surrounding molecular cloud.",
    difficulty=6,
    catalog_ids=["NGC 7635", "Bubble Nebula"]
)

NGC_6888_CRESCENT = Target(
    name="NGC 6888",
    common_name="Crescent Nebula",
    target_type=TargetType.NEBULA,
    ra_hours=20.2000,
    dec_degrees=38.3500,
    magnitude=7.4,
    surface_brightness=10.0,
    angular_size=(25.0, 18.0),
    distance_ly=5000,
    constellation="Cygnus",
    optimal_months=[7, 8, 9, 10],
    seasons=[Season.SUMMER, Season.FALL],
    hemisphere=Hemisphere.NORTHERN,
    equipment=[Equipment.TELEPHOTO, Equipment.MEDIUM_TELESCOPE],
    exposure=ExposureGuideline(
        single_exposure_sec=300,
        total_exposure_min=240,
        iso_gain="ISO 800-1600",
        filters=[FilterRecommendation.NARROWBAND, FilterRecommendation.OIII],
        notes="Narrowband Hubble palette reveals intricate structure."
    ),
    description="Emission nebula formed by fast stellar wind from Wolf-Rayet star colliding "
                "with slower wind from earlier red giant phase. Crescent shape distinctive.",
    difficulty=5,
    catalog_ids=["NGC 6888", "Crescent Nebula", "Caldwell 27"]
)


# ============================================================================
# ADDITIONAL STAR CLUSTERS
# ============================================================================

M35_OPEN_CLUSTER = Target(
    name="M35",
    common_name="M35 Open Cluster",
    target_type=TargetType.STAR_CLUSTER_OPEN,
    ra_hours=6.1458,
    dec_degrees=24.3333,
    magnitude=5.3,
    surface_brightness=None,
    angular_size=(28.0, 28.0),
    distance_ly=2800,
    constellation="Gemini",
    optimal_months=[11, 12, 1, 2, 3],
    seasons=[Season.WINTER],
    hemisphere=Hemisphere.NORTHERN,
    equipment=[Equipment.BINOCULARS, Equipment.SMALL_TELESCOPE],
    exposure=ExposureGuideline(
        single_exposure_sec=120,
        total_exposure_min=60,
        iso_gain="ISO 800",
        filters=[FilterRecommendation.BROADBAND],
        notes="Visible to naked eye under dark skies. Beautiful in binoculars."
    ),
    description="Bright, large open cluster containing ~200 stars. Easily visible to naked eye. "
                "NGC 2158, much older and more distant cluster, appears nearby.",
    difficulty=1,
    catalog_ids=["NGC 2168", "M35"]
)

M37_OPEN_CLUSTER = Target(
    name="M37",
    common_name="M37 Open Cluster",
    target_type=TargetType.STAR_CLUSTER_OPEN,
    ra_hours=5.8692,
    dec_degrees=32.5508,
    magnitude=6.2,
    surface_brightness=None,
    angular_size=(24.0, 24.0),
    distance_ly=4511,
    constellation="Auriga",
    optimal_months=[11, 12, 1, 2, 3],
    seasons=[Season.WINTER],
    hemisphere=Hemisphere.NORTHERN,
    equipment=[Equipment.BINOCULARS, Equipment.SMALL_TELESCOPE],
    exposure=ExposureGuideline(
        single_exposure_sec=120,
        total_exposure_min=60,
        iso_gain="ISO 800",
        filters=[FilterRecommendation.BROADBAND],
        notes="Richest of the Auriga clusters. Over 500 stars."
    ),
    description="Richest and brightest open cluster in Auriga. Contains over 500 stars with "
                "prominent orange giant near center. Age: 347 million years.",
    difficulty=2,
    catalog_ids=["NGC 2099", "M37"]
)

M44_BEEHIVE = Target(
    name="M44",
    common_name="Beehive Cluster",
    target_type=TargetType.STAR_CLUSTER_OPEN,
    ra_hours=8.6667,
    dec_degrees=19.6667,
    magnitude=3.7,
    surface_brightness=None,
    angular_size=(95.0, 95.0),
    distance_ly=610,
    constellation="Cancer",
    optimal_months=[1, 2, 3, 4],
    seasons=[Season.WINTER, Season.SPRING],
    hemisphere=Hemisphere.NORTHERN,
    equipment=[Equipment.NAKED_EYE, Equipment.BINOCULARS, Equipment.WIDE_FIELD],
    exposure=ExposureGuideline(
        single_exposure_sec=60,
        total_exposure_min=30,
        iso_gain="ISO 800",
        filters=[FilterRecommendation.BROADBAND],
        notes="Best in binoculars or wide field. Very large angular size."
    ),
    description="One of the nearest open clusters. Known since ancient times. Contains ~1000 "
                "stars. Visible to naked eye as fuzzy patch between Gemini and Leo.",
    difficulty=1,
    catalog_ids=["NGC 2632", "Beehive Cluster", "Praesepe"]
)

M67_OLD_CLUSTER = Target(
    name="M67",
    common_name="King Cobra Cluster",
    target_type=TargetType.STAR_CLUSTER_OPEN,
    ra_hours=8.8467,
    dec_degrees=11.8167,
    magnitude=6.1,
    surface_brightness=None,
    angular_size=(30.0, 30.0),
    distance_ly=2700,
    constellation="Cancer",
    optimal_months=[1, 2, 3, 4],
    seasons=[Season.WINTER, Season.SPRING],
    hemisphere=Hemisphere.BOTH,
    equipment=[Equipment.BINOCULARS, Equipment.SMALL_TELESCOPE],
    exposure=ExposureGuideline(
        single_exposure_sec=180,
        total_exposure_min=90,
        iso_gain="ISO 800",
        filters=[FilterRecommendation.BROADBAND],
        notes="One of oldest open clusters known. Similar age to solar system."
    ),
    description="Ancient open cluster, ~4 billion years old. Contains ~500 stars. Extensively "
                "studied as it's similar age and metallicity to the Sun.",
    difficulty=2,
    catalog_ids=["NGC 2682", "M67"]
)

JEWEL_BOX_CLUSTER = Target(
    name="NGC 4755",
    common_name="Jewel Box Cluster",
    target_type=TargetType.STAR_CLUSTER_OPEN,
    ra_hours=12.8933,
    dec_degrees=-60.3500,
    magnitude=4.2,
    surface_brightness=None,
    angular_size=(10.0, 10.0),
    distance_ly=6440,
    constellation="Crux",
    optimal_months=[3, 4, 5, 6],
    seasons=[Season.FALL],  # Southern hemisphere
    hemisphere=Hemisphere.SOUTHERN,
    equipment=[Equipment.BINOCULARS, Equipment.SMALL_TELESCOPE],
    exposure=ExposureGuideline(
        single_exposure_sec=60,
        total_exposure_min=30,
        iso_gain="ISO 800",
        filters=[FilterRecommendation.BROADBAND],
        notes="Beautiful color contrast with supergiants. Near Southern Cross."
    ),
    description="One of the youngest known open clusters at 14 million years. Contains several "
                "bright supergiants with contrasting colors, resembling a jewel box.",
    difficulty=1,
    catalog_ids=["NGC 4755", "Kappa Crucis", "Jewel Box", "Caldwell 94"]
)


# ============================================================================
# MAGELLANIC CLOUDS
# ============================================================================

LARGE_MAGELLANIC_CLOUD = Target(
    name="LMC",
    common_name="Large Magellanic Cloud",
    target_type=TargetType.GALAXY,
    ra_hours=5.3833,
    dec_degrees=-69.7561,
    magnitude=0.9,
    surface_brightness=12.5,
    angular_size=(645.0, 550.0),  # arcminutes = ~10 degrees!
    distance_ly=163000,
    constellation="Dorado/Mensa",
    optimal_months=[11, 12, 1, 2, 3],
    seasons=[Season.SUMMER],  # Southern hemisphere
    hemisphere=Hemisphere.SOUTHERN,
    equipment=[Equipment.WIDE_FIELD, Equipment.TELEPHOTO],
    exposure=ExposureGuideline(
        single_exposure_sec=180,
        total_exposure_min=120,
        iso_gain="ISO 1600-3200",
        filters=[FilterRecommendation.BROADBAND],
        notes="Ultra-wide field for full cloud. Telephoto for Tarantula Nebula detail."
    ),
    description="Satellite galaxy of Milky Way, fourth largest in Local Group. Contains "
                "Tarantula Nebula, the most active star-forming region in the Local Group.",
    difficulty=2,
    catalog_ids=["LMC", "ESO 56-115"]
)

SMALL_MAGELLANIC_CLOUD = Target(
    name="SMC",
    common_name="Small Magellanic Cloud",
    target_type=TargetType.GALAXY,
    ra_hours=0.8792,
    dec_degrees=-72.8286,
    magnitude=2.7,
    surface_brightness=14.0,
    angular_size=(320.0, 185.0),  # arcminutes
    distance_ly=200000,
    constellation="Tucana",
    optimal_months=[9, 10, 11, 12, 1],
    seasons=[Season.SPRING, Season.SUMMER],  # Southern hemisphere
    hemisphere=Hemisphere.SOUTHERN,
    equipment=[Equipment.WIDE_FIELD, Equipment.TELEPHOTO],
    exposure=ExposureGuideline(
        single_exposure_sec=180,
        total_exposure_min=120,
        iso_gain="ISO 1600-3200",
        filters=[FilterRecommendation.BROADBAND],
        notes="Wide field essential. Contains globular cluster 47 Tuc in same field."
    ),
    description="Dwarf galaxy companion to Milky Way. Contains over 1 billion stars. "
                "Bridge of gas and stars connects it to LMC.",
    difficulty=2,
    catalog_ids=["SMC", "NGC 292"]
)


# ============================================================================
# CATALOG ASSEMBLY
# ============================================================================

# Master catalog of all targets
ASTRONOMICAL_CATALOG = [
    # Milky Way
    MILKY_WAY_CORE,
    SUMMER_TRIANGLE,

    # Galaxies
    M31_ANDROMEDA,
    M33_TRIANGULUM,
    M51_WHIRLPOOL,
    M81_BODES,
    M82_CIGAR,
    M101_PINWHEEL,
    M63_SUNFLOWER,
    M64_BLACK_EYE,
    M83_SOUTHERN_PINWHEEL,
    M87_VIRGO_A,
    M104_SOMBRERO,
    NGC_253_SCULPTOR,

    # Emission Nebulae
    M42_ORION,
    M8_LAGOON,
    M16_EAGLE,
    M17_OMEGA,
    M20_TRIFID,
    HORSEHEAD_NEBULA,
    CALIFORNIA_NEBULA,
    NORTH_AMERICA_NEBULA,
    VEIL_NEBULA,
    ROSETTE_NEBULA,
    CARINA_NEBULA,
    NGC_7635_BUBBLE,
    NGC_6888_CRESCENT,

    # Planetary Nebulae
    M27_DUMBBELL,
    M57_RING,
    NGC_7293_HELIX,

    # Star Clusters
    M45_PLEIADES,
    M13_HERCULES,
    OMEGA_CENTAURI,
    CLUSTER_47_TUC,
    DOUBLE_CLUSTER,
    M35_OPEN_CLUSTER,
    M37_OPEN_CLUSTER,
    M44_BEEHIVE,
    M67_OLD_CLUSTER,
    JEWEL_BOX_CLUSTER,

    # Planets & Moon
    MOON,
    MERCURY,
    VENUS,
    MARS,
    JUPITER,
    SATURN,
    URANUS,
    NEPTUNE,

    # Magellanic Clouds
    LARGE_MAGELLANIC_CLOUD,
    SMALL_MAGELLANIC_CLOUD,
]


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_targets_by_type(target_type: TargetType) -> List[Target]:
    """Filter catalog by target type."""
    return [t for t in ASTRONOMICAL_CATALOG if t.target_type == target_type]


def get_targets_by_season(season: Season) -> List[Target]:
    """Filter catalog by optimal viewing season."""
    return [t for t in ASTRONOMICAL_CATALOG if season in t.seasons]


def get_targets_by_hemisphere(hemisphere: Hemisphere) -> List[Target]:
    """Filter catalog by observable hemisphere."""
    return [t for t in ASTRONOMICAL_CATALOG
            if t.hemisphere == hemisphere or t.hemisphere == Hemisphere.BOTH]


def get_targets_by_month(month: int) -> List[Target]:
    """Filter catalog by optimal viewing month (1-12)."""
    return [t for t in ASTRONOMICAL_CATALOG if month in t.optimal_months]


def get_targets_by_difficulty(max_difficulty: int) -> List[Target]:
    """Filter catalog by maximum difficulty level."""
    return [t for t in ASTRONOMICAL_CATALOG if t.difficulty <= max_difficulty]


def get_targets_by_equipment(equipment: Equipment) -> List[Target]:
    """Filter catalog by required equipment."""
    return [t for t in ASTRONOMICAL_CATALOG if equipment in t.equipment]


def search_targets(query: str) -> List[Target]:
    """
    Search catalog by name or catalog ID.

    Args:
        query: Search string (case-insensitive)

    Returns:
        List of matching targets
    """
    query_lower = query.lower()
    results = []

    for target in ASTRONOMICAL_CATALOG:
        # Search in name
        if query_lower in target.name.lower():
            results.append(target)
            continue

        # Search in common name
        if query_lower in target.common_name.lower():
            results.append(target)
            continue

        # Search in catalog IDs
        for cat_id in target.catalog_ids:
            if query_lower in cat_id.lower():
                results.append(target)
                break

    return results


def get_tonight_targets(observer_lat: float, date: datetime,
                        max_difficulty: int = 10) -> List[Target]:
    """
    Get targets optimal for tonight's observing session.

    Args:
        observer_lat: Observer's latitude in degrees
        date: Observation date
        max_difficulty: Maximum difficulty level

    Returns:
        List of recommended targets for the date
    """
    month = date.month
    targets = get_targets_by_month(month)

    # Filter by difficulty
    targets = [t for t in targets if t.difficulty <= max_difficulty]

    # Filter by hemisphere
    if observer_lat > 0:
        hemisphere = Hemisphere.NORTHERN
    else:
        hemisphere = Hemisphere.SOUTHERN
    targets = [t for t in targets
               if t.hemisphere == hemisphere or t.hemisphere == Hemisphere.BOTH]

    # Sort by difficulty (easiest first)
    targets.sort(key=lambda t: t.difficulty)

    return targets


def print_target_summary(target: Target) -> str:
    """
    Generate a formatted summary of target information.

    Args:
        target: Target to summarize

    Returns:
        Formatted string with target details
    """
    ra_h, ra_m, ra_s = target.get_ra_hms()
    dec_d, dec_m, dec_s = target.get_dec_dms()

    summary = f"""
{'='*70}
{target.common_name} ({target.name})
{'='*70}
Type: {target.target_type.name}
Constellation: {target.constellation}

Coordinates (J2000):
  RA:  {ra_h:02d}h {ra_m:02d}m {ra_s:05.2f}s
  Dec: {dec_d:+03d}° {dec_m:02d}' {dec_s:05.2f}"

Physical Properties:
  Magnitude: {target.magnitude}
  Surface Brightness: {target.surface_brightness if target.surface_brightness else 'N/A'} mag/arcsec²
  Angular Size: {target.angular_size[0]:.1f}' × {target.angular_size[1]:.1f}'
  Distance: {f'{target.distance_ly:,.0f} ly' if target.distance_ly else 'Variable'}

Observing Info:
  Optimal Months: {', '.join([str(m) for m in target.optimal_months])}
  Seasons: {', '.join([s.value for s in target.seasons])}
  Hemisphere: {target.hemisphere.value}
  Difficulty: {target.difficulty}/10

Equipment:
  {', '.join([e.value for e in target.equipment])}

Imaging:
  Single Exposure: {target.exposure.single_exposure_sec}s
  Total Integration: {target.exposure.total_exposure_min} min
  ISO/Gain: {target.exposure.iso_gain}
  Filters: {', '.join([f.value for f in target.exposure.filters])}
  Notes: {target.exposure.notes}

Description:
  {target.description}

Catalog IDs: {', '.join(target.catalog_ids) if target.catalog_ids else 'None'}
{'='*70}
    """
    return summary


# ============================================================================
# MODULE METADATA
# ============================================================================

__version__ = "1.0.0"
__author__ = "AstroCam Sync Development Team"
__catalog_size__ = len(ASTRONOMICAL_CATALOG)
__target_types__ = len(set(t.target_type for t in ASTRONOMICAL_CATALOG))

# Verify catalog meets requirements
assert __catalog_size__ >= 30, f"Catalog must contain at least 30 targets, has {__catalog_size__}"
