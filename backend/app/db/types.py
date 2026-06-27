from sqlalchemy import Enum as SAEnum

from backend.app.core.enums import (
    ClusterType,
    IncidentCategory,
    JobStatus,
    ReportStatus,
    SeverityLevel,
    UserRole,
)

REPORT_STATUS_ENUM = SAEnum(
    ReportStatus,
    name="report_status",
    native_enum=True,
    validate_strings=True,
)

SEVERITY_LEVEL_ENUM = SAEnum(
    SeverityLevel,
    name="severity_level",
    native_enum=True,
    validate_strings=True,
)

INCIDENT_CATEGORY_ENUM = SAEnum(
    IncidentCategory,
    name="incident_category",
    native_enum=True,
    validate_strings=True,
)

USER_ROLE_ENUM = SAEnum(
    UserRole,
    name="user_role",
    native_enum=True,
    validate_strings=True,
)

CLUSTER_TYPE_ENUM = SAEnum(
    ClusterType,
    name="cluster_type",
    native_enum=True,
    validate_strings=True,
)

JOB_STATUS_ENUM = SAEnum(
    JobStatus,
    name="job_status",
    native_enum=True,
    validate_strings=True,
)