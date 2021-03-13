from dataclasses import dataclass
from typing import Optional, List


@dataclass
class MonitoredResource:
    path: str
    recursive: bool = False


@dataclass
class MonitoredPattern(MonitoredResource):
    patterns: Optional[List[str]] = None
    ignore_patterns: Optional[List[str]] = None
    ignore_directories: Optional[List[str]] = None
    case_sensitive: bool = True


@dataclass
class MonitoredRegex(MonitoredResource):
    regexes: Optional[List[str]] = None
    ignore_regexes: Optional[List[str]] = None
    ignore_directories: Optional[List[str]] = None
    case_sensitive: bool = True
