using System;
using System.Linq;
using Xbim.Common;
using Xbim.Ifc;
using Xbim.Ifc4.Interfaces;
using Xbim.Ifc4.Kernel;
using Xbim.Ifc4.ProductExtension;
using Xbim.Ifc4.SharedBldgElements;
using Xbim.Ifc4.GeometryResource;
using Xbim.Ifc4.RepresentationResource;
using Xbim.Ifc4.MeasureResource;
using Xbim.Ifc4.ProfileResource;
using Xbim.Ifc4.GeometricModelResource;
using Xbim.IO;

class Program
{
    static void Main()
    {
        string ifcFile = "SimpleStructure.ifc";

        using (var model = CreateModel())
        {
            using (var txn = model.BeginTransaction("Add Column and Rafter with Shapes"))
            {
                var project = model.Instances.OfType<IfcProject>().FirstOrDefault();
                if (project == null)
                {
                    throw new Exception("Unable to find the IfcProject instance.");
                }

                // Create site, building, and storey
                var site = model.Instances.New<IfcSite>(s => s.Name = "My Site");
                var building = model.Instances.New<IfcBuilding>(b => b.Name = "My Building");
                var storey = model.Instances.New<IfcBuildingStorey>(s => s.Name = "Ground Floor");

                model.Instances.New<IfcRelAggregates>(r =>
                {
                    r.RelatingObject = project;
                    r.RelatedObjects.Add(site);
                });
                model.Instances.New<IfcRelAggregates>(r =>
                {
                    r.RelatingObject = site;
                    r.RelatedObjects.Add(building);
                });
                model.Instances.New<IfcRelAggregates>(r =>
                {
                    r.RelatingObject = building;
                    r.RelatedObjects.Add(storey);
                });

                // Create column and assign shape
                var column = model.Instances.New<IfcColumn>(c =>
                {
                    c.Name = "Column1";
                    c.PredefinedType = IfcColumnTypeEnum.COLUMN;
                });
                AssignRectangleShape(model, column, 0.3, 0.3, 3.0); // 30cm x 30cm, 3m high

                // Create rafter and assign shape
                var rafter = model.Instances.New<IfcMember>(m =>
                {
                    m.Name = "Rafter1";
                    m.PredefinedType = IfcMemberTypeEnum.RAFTER;
                });
                AssignRectangleShape(model, rafter, 0.2, 0.4, 4.0); // 20cm x 40cm, 4m long

                // Place components into the storey
                model.Instances.New<IfcRelContainedInSpatialStructure>(r =>
                {
                    r.RelatingStructure = storey;
                    r.RelatedElements.Add(column);
                    r.RelatedElements.Add(rafter);
                });

                txn.Commit();
            }

            model.SaveAs(ifcFile, StorageType.Ifc);
            Console.WriteLine($"IFC file saved successfully: {ifcFile}");
        }
    }

    static IfcStore CreateModel()
    {
        var tempFilePath = "temp.ifc";
        var model = IfcStore.Create(tempFilePath, new XbimEditorCredentials
        {
            ApplicationDevelopersName = "MyCompany",
            ApplicationFullName = "MyIFCApp",
            ApplicationIdentifier = "IFC Generator",
            ApplicationVersion = "1.0",
            EditorsFamilyName = "Huang",
            EditorsGivenName = "Jiasheng",
            EditorsOrganisationName = "MyCompany"
        }, Xbim.Common.Step21.XbimSchemaVersion.Ifc4);

        using (var txn = model.BeginTransaction("Project Setup"))
        {
            var project = model.Instances.New<IfcProject>();
            project.Initialize(ProjectUnits.SIUnitsUK);
            txn.Commit();
        }
        return model;
    }

    static void AssignRectangleShape(IfcStore model, IfcProduct product, double width, double depth, double height)
    {
        var context = model.Instances.OfType<IfcGeometricRepresentationContext>().FirstOrDefault();
        if (context == null)
        {
            context = model.Instances.New<IfcGeometricRepresentationContext>(c =>
            {
                c.ContextType = "Model";
                c.CoordinateSpaceDimension = 3;
                c.Precision = 0.00001;
            });
        }

        var shapeRep = model.Instances.New<IfcShapeRepresentation>(r =>
        {
            r.ContextOfItems = context;
            r.RepresentationIdentifier = "Body";
            r.RepresentationType = "SweptSolid";
        });

        var profile = model.Instances.New<IfcRectangleProfileDef>(p =>
        {
            p.ProfileType = IfcProfileTypeEnum.AREA;
            p.XDim = new IfcPositiveLengthMeasure(width);
            p.YDim = new IfcPositiveLengthMeasure(depth);
        });

        var position = model.Instances.New<IfcAxis2Placement3D>(pos =>
        {
            pos.Location = model.Instances.New<IfcCartesianPoint>(pt =>
                pt.Coordinates.AddRange(new IfcLengthMeasure[] { 0.0, 0.0, 0.0 }));
        });

        var solid = model.Instances.New<IfcExtrudedAreaSolid>(s =>
        {
            s.SweptArea = profile;
            s.ExtrudedDirection = model.Instances.New<IfcDirection>(d =>
                d.DirectionRatios.AddRange(new IfcReal[] { 0.0, 0.0, 1.0 }));
            s.Depth = new IfcPositiveLengthMeasure(height);
            s.Position = position;
        });

        shapeRep.Items.Add(solid);

        var productDef = model.Instances.New<IfcProductDefinitionShape>(pds => pds.Representations.Add(shapeRep));

        product.Representation = productDef;
    }
}
