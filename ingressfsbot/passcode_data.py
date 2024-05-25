
import logging
logger = logging.getLogger(__name__)

import json

from dataclasses import dataclass, field, asdict


def load(filename):
    with open(filename, "r") as fp:
        return PasscodeData(**json.load(fp))


def dump(filename, data):
    with open(filename, "w") as fp:
        json.dump(asdict(data), fp)



@dataclass
class PasscodeData:
    image_url: str = ""
    user_reports: dict[str, dict] = field(default_factory=dict)
    user_info: dict[str, dict] = field(default_factory=dict)
    user_trusted: list = field(default_factory=list)

    def get_user_reports(self, uid):
        reports = set()
        for index in self.user_reports[uid]:
            entry = (
                index,
                self.user_reports[uid][index][-1]["name"],
                self.user_reports[uid][index][-1]["media"],
            )
            reports.add(entry)
        return list(reports)

    def get_trustable_reports(self):
        reports = set()
        trusted_reports = set()
        for uid in self.user_reports:
            for index in self.user_reports[uid]:
                entry = (
                    index,
                    self.user_reports[uid][index][-1]["name"],
                    self.user_reports[uid][index][-1]["media"],
                )
                if entry in reports:
                    trusted_reports.add(entry)
                reports.add(entry)
        return list(trusted_reports)
    
    def get_trustable_users(self):
        trusted_users = set()
        trusted_reports = self.get_trustable_reports()
        for uid in self.user_reports:
            user_reports = self.get_user_reports(uid)
            for entry in user_reports:
                if entry in trusted_reports:
                    trusted_users.add(uid)
        return list(trusted_users)
