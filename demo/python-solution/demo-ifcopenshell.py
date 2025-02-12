import ifcopenshell


class IfcElement:
    """ Base class for IFC elements (e.g., columns, rafters) """

    def __init__(self, model, element_type, name, width, depth, height, x, y, z):
        self.model = model
        self.name = name
        self.width = width
        self.depth = depth
        self.height = height
        self.x = x
        self.y = y
        self.z = z
        self.element = model.create_entity(element_type, GlobalId=ifcopenshell.guid.new(), Name=name)
        self.place_element()
        self.assign_rectangle_shape()

    def place_element(self):
        """ Sets the position of the IfcProduct """
        placement = self.model.create_entity("IfcLocalPlacement")

        # Define the coordinate point
        point = self.model.create_entity("IfcCartesianPoint", Coordinates=[float(self.x), float(self.y), float(self.z)])
        axis_placement = self.model.create_entity("IfcAxis2Placement3D", Location=point)

        placement.RelativePlacement = axis_placement
        self.element.ObjectPlacement = placement  # Assign the placement to the element

    def assign_rectangle_shape(self):
        """ Assigns a rectangular profile and extrusion geometry to the IfcProduct """
        context = self.model.create_entity("IfcGeometricRepresentationContext", ContextType="Model")

        # Define a rectangular profile
        profile = self.model.create_entity("IfcRectangleProfileDef", ProfileType="AREA", XDim=self.width, YDim=self.depth)

        # Create an extruded solid geometry
        extruded_solid = self.model.create_entity(
            "IfcExtrudedAreaSolid",
            SweptArea=profile,
            ExtrudedDirection=self.model.create_entity("IfcDirection", DirectionRatios=[0.0, 0.0, 1.0]),
            Depth=self.height
        )

        # Create IfcShapeRepresentation
        shape_rep = self.model.create_entity(
            "IfcShapeRepresentation",
            ContextOfItems=context,
            RepresentationIdentifier="Body",
            RepresentationType="SweptSolid",
            Items=[extruded_solid]
        )

        # Assign IfcProductDefinitionShape to the element
        product_shape = self.model.create_entity("IfcProductDefinitionShape", Representations=[shape_rep])
        self.element.Representation = product_shape


class Column(IfcElement):
    """ Class representing a column in an IFC file """

    def __init__(self, model, name="Column1", width=0.3, depth=0.3, height=3.0, x=0.0, y=0.0, z=0.0):
        super().__init__(model, "IfcColumn", name, width, depth, height, x, y, z)


class Rafter(IfcElement):
    """ Class representing a rafter in an IFC file """

    def __init__(self, model, name="Rafter1", width=0.2, depth=0.4, height=4.0, x=2.0, y=0.0, z=3.0):
        super().__init__(model, "IfcMember", name, width, depth, height, x, y, z)


def create_ifc_file():
    """ Creates an IFC file with a column and a rafter """
    # Create a new IFC file
    model = ifcopenshell.file()

    # Create IfcProject
    project = model.create_entity("IfcProject", GlobalId=ifcopenshell.guid.new(), Name="My IFC Project")

    # Set up units
    unit_assignment = model.create_entity("IfcUnitAssignment")
    length_unit = model.create_entity("IfcSIUnit", UnitType="LENGTHUNIT", Name="METRE")
    unit_assignment.Units = [length_unit]
    project.UnitsInContext = unit_assignment  # Assign units to the project

    # Create IfcSite, IfcBuilding, and IfcBuildingStorey
    site = model.create_entity("IfcSite", GlobalId=ifcopenshell.guid.new(), Name="My Site")
    building = model.create_entity("IfcBuilding", GlobalId=ifcopenshell.guid.new(), Name="My Building")
    storey = model.create_entity("IfcBuildingStorey", GlobalId=ifcopenshell.guid.new(), Name="Ground Floor")

    # Establish hierarchical relationships (Project → Site → Building → Storey)
    model.create_entity("IfcRelAggregates", GlobalId=ifcopenshell.guid.new(), RelatingObject=project,
                        RelatedObjects=[site])
    model.create_entity("IfcRelAggregates", GlobalId=ifcopenshell.guid.new(), RelatingObject=site,
                        RelatedObjects=[building])
    model.create_entity("IfcRelAggregates", GlobalId=ifcopenshell.guid.new(), RelatingObject=building,
                        RelatedObjects=[storey])

    # Create a column and a rafter
    column = Column(model)
    rafter = Rafter(model)

    # Assign the column and rafter to the storey
    model.create_entity("IfcRelContainedInSpatialStructure",
                        GlobalId=ifcopenshell.guid.new(),
                        RelatingStructure=storey,
                        RelatedElements=[column.element, rafter.element])

    # Save the IFC file
    ifc_filename = "generated_structure.ifc"
    model.write(ifc_filename)
    print(f"IFC file successfully generated: {ifc_filename}")


# Execute
create_ifc_file()
