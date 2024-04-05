# myapp/management/commands/hello.py
from django.core.management.base import BaseCommand, CommandParser
from faker import Faker
from core.models import AreaCoverage, System, SystemStatus, Images, SystemFumigation, SystemWaterLevel
from datetime import timedelta
from django.utils import timezone

class Command(BaseCommand):
    help = 'Prints "Hello, World!" to the console'

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument('--area_count', default=3, type=int, help='The number of area entries to generate')
        parser.add_argument('--system_count', default=5, type=int, help='The number of system entries to generate')
        parser.add_argument('--system_status_count', default=100, type=int, help='The number of system status entries to generate')
        parser.add_argument('--image_count', default=1000, type=int, help='The number of image entries to generate')
        parser.add_argument('--fumigation_count', default=100, type=int, help='The number of fumigation entries to generate')
        parser.add_argument('--water_level_count', default=100, type=int, help='The number of water level entries to generate')

    def handle(self, *args, **options):
        fake = Faker()

        area_count = options['area_count']

        for _ in range(area_count):
            area_name = fake.address()
            area_description = fake.text()
            image = fake.image_url()
            area_latitude = fake.latitude()
            area_longitude = fake.longitude()

            AreaCoverage.objects.create(
                area_name=area_name,
                description=area_description,
                image=image,
                area_latitude=area_latitude,
                area_longitude=area_longitude
            )
        self.stdout.write(f"Successfully created {area_count} area entries.")

        areas = AreaCoverage.objects.all()

        for _ in range(options['system_count']):
            secret_key = fake.uuid4()
            name = fake.company()
            description = fake.text()
            image = fake.image_url()
            coverage = fake.random_element(areas)
            location_name = fake.address()
            location_latitude = fake.latitude()
            location_longitude = fake.longitude()
            location_radius = fake.random_int(10, 100)

            System.objects.create(
                secret_key=secret_key,
                name=name,
                description=description,
                image=image,
                coverage=coverage,
                location_name=location_name,
                location_latitude=location_latitude,
                location_longitude=location_longitude,
                location_radius=location_radius
            )
        self.stdout.write(f"Successfully created {options['system_count']} system entries.")

        systems = System.objects.all()
        for _ in range(options['system_status_count']):
            system = fake.random_element(systems)
            status = fake.boolean()
            last_updated = fake.date_time_this_year()
            SystemStatus.objects.create(
                system=system,
                status=status,
                last_updated=last_updated
            )
        self.stdout.write(f"Successfully created {options['system_status_count']} system status entries.")

        images = [
            "mosquitoes/mosquitoes_system_1_2023-12-08T193733.272655.jpg",
            "mosquitoes/mosquitoes_system_1_2023-12-08T193809.742889.jpg",
            "mosquitoes/mosquitoes_system_1_2023-12-08T193958.340010.jpg",
            "mosquitoes/433697814_392202480344703_433288004452797183_n.jpg",
        ]
        for _ in range(options['image_count']):
            system = fake.random_element(systems)
            area = fake.random_element(areas)
            photo = fake.random_element(images)

            print(photo)

            now = timezone.now()
            hour_ago = now - timedelta(hours=1)

            date_uploaded = fake.date_time_between_dates(datetime_start=hour_ago, datetime_end=now)
            detected_moquito_acount = fake.random_int(1, 100)
            prediction_time = fake.random_int(1, 100)

            obj = Images.objects.create(
                system=system,
                area=area,
                photo=photo,
                date_uploaded=date_uploaded,
                detected_mosquito_count=detected_moquito_acount,
                prediction_time=prediction_time
            )

            obj.date_uploaded = date_uploaded
            obj.save()

        self.stdout.write(f"Successfully created {options['image_count']} image entries.")

        for _ in range(options['fumigation_count']):
            system = fake.random_element(systems)
            fumigation_date = fake.date_time_this_year()

            SystemFumigation.objects.create(
                system=system,
                fumigation_date=fumigation_date
            )
        self.stdout.write(f"Successfully created {options['fumigation_count']} fumigation entries.")

        for _ in range(options['water_level_count']):
            system = fake.random_element(systems)
            water_level = fake.random_int(1, 100)
            last_updated = fake.date_time_this_year()

            SystemWaterLevel.objects.create(
                system=system,
                water_level=water_level,
                last_updated=last_updated
            )
        self.stdout.write(f"Successfully created {options['water_level_count']} water level entries.")


        
            





        
