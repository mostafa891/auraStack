from apps.users.models import CustomUser


def run():
    print("Starting database seeding...")

    # Create or update demo superuser
    admin_email = "admin@aurastack.com"
    admin_user, created = CustomUser.objects.get_or_create(
        email=admin_email,
        defaults={
            "first_name": "Aura",
            "last_name": "Admin",
            "is_staff": True,
            "is_superuser": True,
            "is_active": True,
            "language": "en",
            "theme": "DARK",
            "timezone": "UTC",
        },
    )
    if created or not admin_user.has_usable_password():
        admin_user.set_password("AdminPass123!")
        admin_user.save()
        print(f"[*] Superuser created/updated: {admin_email} (Password: AdminPass123!)")
    else:
        print(f"[-] Superuser already exists: {admin_email}")

    # Create or update demo standard user
    user_email = "user@aurastack.com"
    normal_user, created = CustomUser.objects.get_or_create(
        email=user_email,
        defaults={
            "first_name": "Aura",
            "last_name": "User",
            "is_staff": False,
            "is_superuser": False,
            "is_active": True,
            "language": "en",
            "theme": "SYSTEM",
            "timezone": "UTC",
        },
    )
    if created or not normal_user.has_usable_password():
        normal_user.set_password("UserPass123!")
        normal_user.save()
        print(f"[*] Standard user created/updated: {user_email} (Password: UserPass123!)")
    else:
        print(f"[-] Standard user already exists: {user_email}")

    print("[+] Database seeding completed successfully.")
