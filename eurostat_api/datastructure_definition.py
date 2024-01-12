import xml.etree.ElementTree as et
from typing import Dict, List


class DatastructureDefinition:

    M_URI: str = "http://www.sdmx.org/resources/sdmxml/schemas/v3_0/message"
    S_URI: str = "http://www.sdmx.org/resources/sdmxml/schemas/v3_0/structure"

    PREFIX_MAP: Dict[str, str] = {
        'm': M_URI,
        's': S_URI
    }

    _root: et.Element
    _dimension_ids: List[str]

    def __init__(self, xml_source: str):
        self._root = et.fromstring(xml_source)
        dimension_list = self._root.find("/".join((
            './/m:Structures',
            './/s:DataStructures',
            './/s:DataStructure',
            './/s:DataStructureComponents',
            './/s:DimensionList'
        )), self.PREFIX_MAP)
        ids_with_positions = [
            (dimension.get('id'), dimension.get('position'))
            for dimension in dimension_list.findall(
                './/s:Dimension', self.PREFIX_MAP
            )
        ]
        ids_with_positions.sort(key=lambda x: x[0])
        self._dimension_ids = [id for id, _ in ids_with_positions]

    @property
    def dimension_ids(self) -> List[str]:
        return self._dimension_ids
