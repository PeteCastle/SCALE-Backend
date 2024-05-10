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

        barangays = [
            {
                "area_name": "Barangay San Antonio, Makati City",
                "area_description": "Located in the heart of Makati's central business district, Barangay San Antonio is a bustling urban area characterized by high-rise buildings, commercial establishments, and residential condominiums. Despite its urban setting, the Barangay faces challenges with mosquito infestations due to the presence of pockets of stagnant water and densely populated residential areas.",
                "image": "",
                "area_latitude": -14.565681665533202,
                "area_longitude": 121.00889322738335
            },
            {
                "area_name": "Barangay Pio del Pilar, Makati City",
                "area_description": "Barangay Pio del Pilar is a mixed-use area in Makati City, known for its residential communities, commercial establishments, and educational institutions. The Barangay experiences mosquito-related issues, especially during the rainy season, as inadequate drainage systems and improper waste management contribute to breeding grounds for mosquitoes.",
                "image": "",
                "area_latitude": -14.549759729148162,
                "area_longitude": 121.01225016475254
            },
            {
                "area_name": "Barangay Bagong Lipunan ng Crame, Quezon City",
                "area_description": "Situated in Quezon City, Barangay Bagong Lipunan ng Crame is a dynamic urban area with a mix of residential and commercial zones. Despite efforts to address sanitation and waste management, the Barangay contends with mosquito infestations, particularly in areas with poor drainage and sanitation facilities.",
                "image": "",
                "area_latitude": -14.613598970713864,
                "area_longitude": 121.05367204307743
            },
            {
                "area_name": "Barangay Commonwealth, Quezon City",
                "area_description": "Barangay Commonwealth is one of the largest Barangays in Quezon City, characterized by residential subdivisions, commercial centers, and educational institutions. The Barangay faces challenges with mosquitoes, especially in low-lying areas prone to flooding, where stagnant water accumulates during the rainy season.",
                "image": "",
                "area_latitude": -14.697907817242996,
                "area_longitude": 121.08533870368937
            },
            {
                "area_name": "Barangay South Triangle, Quezon City",
                "area_description": "Located near the heart of Quezon City's entertainment and commercial district, Barangay South Triangle is a vibrant community with residential condominiums, offices, and retail establishments. Mosquito-related issues arise in the Barangay due to factors such as improper waste disposal and inadequate drainage systems.",
                "image": "",
                "area_latitude": -14.638323387153637,
                "area_longitude": 121.03613022237455
            },
            {
                "area_name": "Barangay Poblacion, Makati City",
                "area_description": "Barangay Poblacion is the historic core of Makati City, known for its mix of residential, commercial, and cultural attractions. Despite its bustling atmosphere, the Barangay faces challenges with mosquitoes, particularly in densely populated residential areas and informal settlements.",
                "image": "",
                "area_latitude": -14.565155492710943,
                "area_longitude": 121.03579825350825
            },
            {
                "area_name": "Barangay Addition Hills, Mandaluyong City",
                "area_description": "Barangay Addition Hills is a predominantly residential area in Mandaluyong City, characterized by mid-rise condominiums and residential subdivisions. Mosquito-related issues in the Barangay stem from factors like poor waste management and insufficient drainage systems, especially in areas prone to flooding.",
                "image": "",
                "area_latitude": -14.58322455737419,
                "area_longitude": 121.03708592465844
            },
            {
                "area_name": "Barangay San Isidro, Makati City",
                "area_description": "Located in the northern part of Makati City, Barangay San Isidro is a predominantly residential area with pockets of commercial establishments. The Barangay contends with mosquito infestations, particularly in areas with poor drainage and sanitation infrastructure.",
                "image": "",
                "area_latitude": -14.554150101176141,
                "area_longitude": 121.00364406177926
            },
            {
                "area_name": "Barangay Holy Spirit, Quezon City",
                "area_description": "Barangay Holy Spirit is a suburban area in Quezon City, characterized by residential subdivisions, schools, and religious institutions. Despite its relatively green surroundings, the Barangay faces challenges with mosquitoes, especially during the rainy season when stagnant water accumulates in open spaces and drainage channels.",
                "image": "",
                "area_latitude": -14.68488393004743,
                "area_longitude": 121.07709837027866
            },
            {
                "area_name": "Barangay Batasan Hills, Quezon City",
                "area_description": "Situated in the eastern part of Quezon City, Barangay Batasan Hills is a residential community known for its hilly terrain and suburban atmosphere. Mosquito-related issues in the Barangay are exacerbated by factors such as inadequate waste management and irregular fumigation efforts, particularly in densely populated areas.",
                "image": "",
                "area_latitude": -14.685355623919113,
                "area_longitude": 121.09811210483159
            },
            {
                "area_name": "Barangay Dagupan, Tondo, Manila",
                "area_description":"Barangay Dagupan is situated in the district of Tondo, Manila, known for its bustling urban environment and vibrant community life. The Barangay is characterized by densely populated residential areas, bustling markets, and various commercial establishments. Despite its vibrant atmosphere, Barangay Dagupan faces challenges related to sanitation and waste management, which can contribute to mosquito infestations, particularly during the rainy season. The community actively engages in various initiatives to address these issues, including regular cleanup drives and awareness campaigns on proper waste disposal. Residents of Barangay Dagupan work together to create a cleaner and healthier environment for all members of the community.",
                "image": "",
                "area_latitude": 14.615116690653338,
                "area_longitude": 120.97193330521904
            }
        ]

        AreaCoverage.objects.bulk_create([
            AreaCoverage(
                area_name=barangay['area_name'],
                description=barangay['area_description'],
                image=barangay['image'],
                area_latitude=barangay['area_latitude'],
                area_longitude=barangay['area_longitude']
            )
            for barangay in barangays
        ])
        
        self.stdout.write(f"Successfully created {len(barangays)} area entries.")

        areas = AreaCoverage.objects.all()

        systems = [
            {
                "secret_key" : fake.uuid4(),
                "name": "Kalayaan B Street System",
                "description": "The Kalayaan B Street System is a mosquito monitoring system located in Barangay Batasan Hills, Quezon City",
                "coverage" : AreaCoverage.objects.get(area_name="Barangay Batasan Hills, Quezon City"),
                "location_name": "270 Kalayaan B, Quezon City, 1126 Metro Manila",
                "location_latitude": 14.690344349946951, 
                "location_longitude": 121.09174044669045,
                "location_radius": 50,
                "image": "system/system_sample_1.jpg"
            },
            {
                "secret_key" : fake.uuid4(),
                "name": "Faraday Street System",
                "description": "The Faraday Street System is a mosquito monitoring system located in Barangay San Isidro, Makati City",
                "coverage" : AreaCoverage.objects.get(area_name="Barangay San Isidro, Makati City"),
                "location_name": "Faraday St, Makati, San Isidro, Makati, Metro Manila",
                "location_latitude": 14.554235189503201, 
                "location_longitude": 121.00484233859548,
                "location_radius": 45,
                "image": "system/system_sample_2.jpg",
            },
            {
                "secret_key" : fake.uuid4(),
                "name": "Poblacion Boat Station",
                "description": "The Poblacion Boat Station is a mosquito monitoring system located in Barangay Poblacion, Makati City",
                "coverage" : AreaCoverage.objects.get(area_name="Barangay Poblacion, Makati City"),
                "location_name": "Poblacion, Makati, Metro Manila",
                "location_latitude": 14.568007059592038,
                "location_longitude":  121.03275858586959,
                "location_radius": 42,
                "image": "system/system_sample_3.jpg"
            },
            {
                "secret_key" : fake.uuid4(),
                "name": "Perfecto Street -  Estero De Vitas",
                "description": "The Perfecto Street - Estero De Vitas System is a mosquito monitoring system located in Barangay Dagupan, Tondo, Manila",
                "coverage" : AreaCoverage.objects.get(area_name="Barangay Dagupan, Tondo, Manila"),
                "location_name": "Perfecto St, Tondo, Manila, Metro Manila",
                "location_latitude": 14.612490186517887,
                "location_longitude": 120.9713349470584,
                "location_radius": 60,
                "image": "system/system_sample_4.jpg"
            }

        ]

        System.objects.bulk_create([
            System(
                secret_key=system['secret_key'],
                name=system['name'],
                description=system['description'],
                coverage=system['coverage'],
                location_name=system['location_name'],
                location_latitude=system['location_latitude'],
                location_longitude=system['location_longitude'],
                location_radius=system['location_radius'],
                image=system['image']
            )
            for system in systems
        ])
        self.stdout.write(f"Successfully created {len(systems)} system entries.")

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


        
            





        
