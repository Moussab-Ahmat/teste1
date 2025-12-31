from decimal import Decimal
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='DeliveryZone',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('description', models.TextField(blank=True)),
            ],
            options={'ordering': ['name']},
        ),
        migrations.CreateModel(
            name='DeliverySlot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                (
                    'day_of_week',
                    models.IntegerField(
                        choices=[
                            (0, 'Monday'),
                            (1, 'Tuesday'),
                            (2, 'Wednesday'),
                            (3, 'Thursday'),
                            (4, 'Friday'),
                            (5, 'Saturday'),
                            (6, 'Sunday'),
                        ]
                    ),
                ),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('is_active', models.BooleanField(default=True)),
                (
                    'zone',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='slots',
                        to='delivery.deliveryzone',
                    ),
                ),
            ],
            options={'ordering': ['zone_id', 'day_of_week', 'start_time']},
        ),
        migrations.CreateModel(
            name='DeliveryFeeRule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('min_cart_total_xaf', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=12)),
                ('max_cart_total_xaf', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('delivery_fee_xaf', models.DecimalField(decimal_places=2, max_digits=12)),
                (
                    'zone',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='fee_rules',
                        to='delivery.deliveryzone',
                    ),
                ),
            ],
            options={'ordering': ['zone_id', 'min_cart_total_xaf', 'max_cart_total_xaf']},
        ),
        migrations.AddConstraint(
            model_name='deliveryfeerule',
            constraint=migrations.constraints.CheckConstraint(
                check=models.Q(('max_cart_total_xaf__isnull', True)) | models.Q(('max_cart_total_xaf__gt', models.F('min_cart_total_xaf'))),
                name='delivery_fee_rule_range_valid',
            ),
        ),
    ]
