from typing import Optional

from platypush.message.event import Event


class TravisciBuildEvent(Event):
    def __init__(self,
                 repository_id: int,
                 repository_name: str,
                 repository_slug: str,
                 passed: bool,
                 build_id: int,
                 build_number: int,
                 duration: int,
                 previous_state: str,
                 private: bool,
                 tag: Optional[str],
                 branch: str,
                 commit_id: Optional[str],
                 commit_sha: Optional[str],
                 commit_message: Optional[str],
                 committed_at: str,
                 created_by: str,
                 started_at: str,
                 finished_at: str,
                 *args,
                 **kwargs):
        super().__init__(*args,
                         repository_id=repository_id,
                         repository_name=repository_name,
                         repository_slug=repository_slug,
                         passed=passed,
                         build_id=build_id,
                         build_number=build_number,
                         duration=duration,
                         previous_state=previous_state,
                         private=private,
                         tag=tag,
                         branch=branch,
                         commit_id=commit_id,
                         commit_sha=commit_sha,
                         commit_message=commit_message,
                         committed_at=committed_at,
                         created_by=created_by,
                         started_at=started_at,
                         finished_at=finished_at,
                         **kwargs)


class TravisciBuildPassedEvent(TravisciBuildEvent):
    """
    Event triggered when a Travis-Ci build passes.
    """
    def __init__(self, *args, **kwargs):
        kwargs['passed'] = True
        super().__init__(*args, **kwargs)


class TravisciBuildFailedEvent(TravisciBuildEvent):
    """
    Event triggered when a Travis-Ci build fails.
    """
    def __init__(self, *args, **kwargs):
        kwargs['passed'] = False
        super().__init__(*args, **kwargs)


# vim:sw=4:ts=4:et:
