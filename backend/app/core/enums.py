from enum import Enum


class ReportStatus(str, Enum):
    RECEIVED = "RECEIVED"
    IN_REVIEW = "IN_REVIEW"
    FORWARDED = "FORWARDED"
    RESOLVED = "RESOLVED"
    ARCHIVED = "ARCHIVED"


class SeverityLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class IncidentCategory(str, Enum):
    VERBAL_HARASSMENT = "VERBAL_HARASSMENT"
    DISCRIMINATION = "DISCRIMINATION"
    INTIMIDATION = "INTIMIDATION"
    EXCLUSION = "EXCLUSION"
    THREAT = "THREAT"
    INAPPROPRIATE_PHYSICAL_CONTACT = "INAPPROPRIATE_PHYSICAL_CONTACT"
    OTHER = "OTHER"


class UserRole(str, Enum):
    ADMIN = "ADMIN"
    GESTOR = "GESTOR"


class ClusterType(str, Enum):
    TEXTUAL = "TEXTUAL"
    SPATIAL = "SPATIAL"
    TEMPORAL = "TEMPORAL"
    HYBRID = "HYBRID"


class JobStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    RETRYING = "RETRYING"


class TargetType(str, Enum):
    REPORT = "REPORT"
    USER = "USER"
    TRIAGE_RESULT = "TRIAGE_RESULT"
    NOTE = "NOTE"
    CLUSTER = "CLUSTER"
    JOB = "JOB"
    INSTITUTION_AREA = "INSTITUTION_AREA"