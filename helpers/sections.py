from models.sections import SectionsModel
from models.centers import CentersModel
from common.database import DatabaseConnection


class SectionsHelper:

    @staticmethod
    def get_breadcrumbs(center_id, section_id=None) -> str:
        session = DatabaseConnection()
        separator = " -> "
        center = session.query(CentersModel).filter_by(id=center_id).first()
        result = center.name

        if not section_id:
            return result

        sections = []
        parent = SectionsHelper.get_parent(section_id)
        while parent:
            sections.append(parent.name)
            parent = SectionsHelper.get_parent(parent.parent_id)

        for section_name in reversed(sections):
            result += separator + section_name

        return result

    @staticmethod
    def get_parent(section_id) -> SectionsModel:
        return DatabaseConnection().query(SectionsModel).filter_by(id=section_id).first()
