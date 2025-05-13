from django.core.management.base import BaseCommand
from sportscomplex.models import Facility, PaymentRates, FacilityAvailabilityType, UserTypeRate, UserTypes, FacilityCapacity, FacilityCooldown

class Command(BaseCommand):
    help = 'Populate facility rates, user type-specific rates, capacity, and cooldown values for the Sports Complex'

    def handle(self, *args, **kwargs):
        # ===== PART 1: FACILITY RATES ===== 
        self.stdout.write('Populating standard facility rates...')
        
        # Clear existing rates to avoid duplicates
        PaymentRates.objects.all().delete()
        
        # Get or create facilities
        # Swimming - membership only 
        swimming, _ = Facility.objects.get_or_create(
            facility_name='swimming',
            defaults={
                'availability_type': FacilityAvailabilityType.MEMBERSHIP_ONLY,
                'capacity': None,
                'cooldown_time': None
            }
        )
        swimming.availability_type = FacilityAvailabilityType.MEMBERSHIP_ONLY
        swimming.capacity = None
        swimming.cooldown_time = None
        swimming.save()
        
        # Gym - membership only
        gym, _ = Facility.objects.get_or_create(
            facility_name='gym',
            defaults={
                'availability_type': FacilityAvailabilityType.MEMBERSHIP_ONLY,
                'capacity': None,
                'cooldown_time': None
            }
        )
        gym.availability_type = FacilityAvailabilityType.MEMBERSHIP_ONLY
        gym.capacity = None
        gym.cooldown_time = None
        gym.save()
        
        # Bowling - booking only (800rs)
        bowling, _ = Facility.objects.get_or_create(
            facility_name='bowling',
            defaults={
                'availability_type': FacilityAvailabilityType.BOOKING_ONLY,
                'capacity': FacilityCapacity.BOWLING,
                'cooldown_time': FacilityCooldown.BOWLING
            }
        )
        bowling.availability_type = FacilityAvailabilityType.BOOKING_ONLY
        bowling.capacity = FacilityCapacity.BOWLING
        bowling.cooldown_time = FacilityCooldown.BOWLING
        bowling.save()
        
        # Pool - booking only (free)
        pool, _ = Facility.objects.get_or_create(
            facility_name='pool',
            defaults={
                'availability_type': FacilityAvailabilityType.BOOKING_ONLY,
                'capacity': FacilityCapacity.POOL,
                'cooldown_time': FacilityCooldown.POOL
            }
        )
        pool.availability_type = FacilityAvailabilityType.BOOKING_ONLY
        pool.capacity = FacilityCapacity.POOL
        pool.cooldown_time = FacilityCooldown.POOL
        pool.save()
        
        # Table tennis - booking only (free)
        table_tennis, _ = Facility.objects.get_or_create(
            facility_name='table tennis',
            defaults={
                'availability_type': FacilityAvailabilityType.BOOKING_ONLY,
                'capacity': FacilityCapacity.TABLE_TENNIS,
                'cooldown_time': FacilityCooldown.TABLE_TENNIS
            }
        )
        table_tennis.availability_type = FacilityAvailabilityType.BOOKING_ONLY
        table_tennis.capacity = FacilityCapacity.TABLE_TENNIS
        table_tennis.cooldown_time = FacilityCooldown.TABLE_TENNIS
        table_tennis.save()
        
        # Create rates for each facility
        PaymentRates.objects.create(
            facility=swimming,
            membership_rate=1000,  # 1000rs per month (default rate)
            per_booking_rate=None
        )
        
        PaymentRates.objects.create(
            facility=gym,
            membership_rate=1000,  # 1000rs per month (default rate)
            per_booking_rate=None
        )
        
        PaymentRates.objects.create(
            facility=bowling,
            membership_rate=None,
            per_booking_rate=800  # 800rs per booking
        )
        
        PaymentRates.objects.create(
            facility=pool,
            membership_rate=None,
            per_booking_rate=0  # Free
        )
        
        PaymentRates.objects.create(
            facility=table_tennis,
            membership_rate=None,
            per_booking_rate=0  # Free
        )
        
        self.stdout.write(self.style.SUCCESS('Successfully populated standard facility rates'))
        
        # ===== PART 2: USER TYPE-SPECIFIC RATES ===== BUSINESS RULE !!!!!!!!!
        self.stdout.write('Populating user type-specific rates...')
        
        # Clear existing user type rates to avoid duplicates
        UserTypeRate.objects.all().delete()
        
        # Create rates for each user type based on the pricing chart
        
        # Students (NUST Residents)
        UserTypeRate.objects.create(
            user_type=UserTypes.STUDENT,  # 'student'
            swimming_rate=1000,
            gym_rate=1000,
            master_card_rate=1500,  # Combined rate for swimming + gym
            registration_fee=2000  
        )
        
        # Faculty/Officers
        UserTypeRate.objects.create(
            user_type=UserTypes.FACULTY,  # 'faculty'
            swimming_rate=2000,
            gym_rate=2000,
            master_card_rate=2500,
            registration_fee=3000  
        )
        
        # Alumni
        UserTypeRate.objects.create(
            user_type=UserTypes.ALUMNI,  # 'alumni' 
            swimming_rate=3000,
            gym_rate=3000,
            master_card_rate=4000,
            registration_fee=5000  
        )
        
        # NSTP Tenants (Pakistani)
        UserTypeRate.objects.create(
            user_type=UserTypes.NSTP_TENANT_PAKISTANI,  # 'nstp resident pakistani'
            swimming_rate=5000,
            gym_rate=5000, 
            master_card_rate=8000,
            registration_fee=10000  
        )
        
        # NSTP Tenants (Foreign)
        UserTypeRate.objects.create(
            user_type=UserTypes.NSTP_TENANT_FOREIGN,  # 'nstp resident foreign'
            swimming_rate=10000,
            gym_rate=10000,
            master_card_rate=15000,
            registration_fee=20000  
        )
        
        self.stdout.write(self.style.SUCCESS('Successfully populated user type-specific rates'))
        
        # ===== PART 3: FACILITY CAPACITY AND COOLDOWN =====
        self.stdout.write('Populating facility capacity and cooldown values...')
        
        # Mapping of facility names to their capacity and cooldown values
        facility_configs = {
            'bowling': {
                'capacity': FacilityCapacity.BOWLING,  # '4'
                'cooldown': FacilityCooldown.BOWLING,  # 'B60'
            },
            'pool': {
                'capacity': FacilityCapacity.POOL,     # '3'
                'cooldown': FacilityCooldown.POOL,     # 'P60'
            },
            'table tennis': {
                'capacity': FacilityCapacity.TABLE_TENNIS,  # '2'
                'cooldown': FacilityCooldown.TABLE_TENNIS,  # 'T30'
            },
        }

        # Update each facility
        for facility_name, config in facility_configs.items():
            try:
                facility = Facility.objects.get(facility_name=facility_name)
                facility.capacity = config['capacity']
                facility.cooldown_time = config['cooldown']
                facility.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully updated {facility_name} with capacity={config["capacity"]} and cooldown={config["cooldown"]}'
                    )
                )
            except Facility.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(
                        f'Facility {facility_name} not found'
                    )
                )

        self.stdout.write(self.style.SUCCESS('Successfully populated facility capacity and cooldown values'))
        
        # Overall success message
        self.stdout.write(self.style.SUCCESS('✅ All rate data has been successfully populated!'))