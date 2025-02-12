import ifcopenshell


def create_ifc_file():
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

    # Create a column (IfcColumn) positioned at (0,0,0)
    column = model.create_entity("IfcColumn", GlobalId=ifcopenshell.guid.new(), Name="Column1")
    place_element(model, column, x=0.0, y=0.0, z=0.0)  # Position at the origin
    assign_rectangle_shape(model, column, 0.3, 0.3, 3.0)  # 30cm x 30cm, 3m height

    # Create a rafter (IfcMember) positioned at (2,0,3)
    rafter = model.create_entity("IfcMember", GlobalId=ifcopenshell.guid.new(), Name="Rafter1")
    place_element(model, rafter, x=2.0, y=0.0, z=3.0)  # Shift to X=2m, Z=3m
    assign_rectangle_shape(model, rafter, 0.2, 0.4, 4.0)  # 20cm x 40cm, 4m length

    # Assign the column and rafter to the storey
    model.create_entity("IfcRelContainedInSpatialStructure",
                        GlobalId=ifcopenshell.guid.new(),
                        RelatingStructure=storey,
                        RelatedElements=[column, rafter])

    # Save the IFC file
    ifc_filename = "generated_structure.ifc"
    model.write(ifc_filename)
    print(f"IFC file successfully generated: {ifc_filename}")


def place_element(model, element, x=0.0, y=0.0, z=0.0):
    """ Sets the position of an IfcProduct (e.g., IfcColumn, IfcMember) """
    placement = model.create_entity("IfcLocalPlacement")

    # Define the coordinate point, ensuring the values are floats
    point = model.create_entity("IfcCartesianPoint", Coordinates=[float(x), float(y), float(z)])
    axis_placement = model.create_entity("IfcAxis2Placement3D", Location=point)

    placement.RelativePlacement = axis_placement
    element.ObjectPlacement = placement  # Assign the placement to the element


def assign_rectangle_shape(model, element, width, depth, height):
    """ Assigns a rectangular profile and extrusion geometry to an IfcProduct """
    context = model.create_entity("IfcGeometricRepresentationContext", ContextType="Model")

    # Define a rectangular profile
    profile = model.create_entity("IfcRectangleProfileDef", ProfileType="AREA", XDim=width, YDim=depth)

    # Create an extruded solid geometry
    extruded_solid = model.create_entity(
        "IfcExtrudedAreaSolid",
        SweptArea=profile,
        ExtrudedDirection=model.create_entity("IfcDirection", DirectionRatios=[0.0, 0.0, 1.0]),
        Depth=height
    )

    # Create IfcShapeRepresentation
    shape_rep = model.create_entity(
        "IfcShapeRepresentation",
        ContextOfItems=context,
        RepresentationIdentifier="Body",
        RepresentationType="SweptSolid",
        Items=[extruded_solid]
    )

    # Assign IfcProductDefinitionShape to the element
    product_shape = model.create_entity("IfcProductDefinitionShape", Representations=[shape_rep])
    element.Representation = product_shape


# Execute
create_ifc_file()
