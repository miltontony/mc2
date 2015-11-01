# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('organizations', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AppType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256, null=True, blank=True)),
                ('docker_image', models.CharField(max_length=256, null=True, blank=True)),
                ('title', models.TextField(null=True, blank=True)),
                ('project_type', models.CharField(default=b'unicore-cms', max_length=256, choices=[(b'unicore-cms', b'unicore-cms'), (b'springboard', b'springboard')])),
            ],
            options={
                'ordering': ('title',),
            },
        ),
        migrations.CreateModel(
            name='Localisation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('country_code', models.CharField(help_text=b'See http://www.worldatlas.com/aatlas/ctycodes.htm for reference.', max_length=2, verbose_name='2 letter country code')),
                ('language_code', models.CharField(help_text=b'See http://www.loc.gov/standards/iso639-2/php/code_list.php for reference.', max_length=3, verbose_name='3 letter language code')),
            ],
            options={
                'ordering': ('language_code',),
            },
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('country', models.CharField(max_length=256, choices=[(b'AF', b'Afghanistan'), (b'AX', b'Aland Islands'), (b'AL', b'Albania'), (b'DZ', b'Algeria'), (b'AS', b'American Samoa'), (b'AD', b'AndorrA'), (b'AO', b'Angola'), (b'AI', b'Anguilla'), (b'AQ', b'Antarctica'), (b'AG', b'Antigua and Barbuda'), (b'AR', b'Argentina'), (b'AM', b'Armenia'), (b'AW', b'Aruba'), (b'AU', b'Australia'), (b'AT', b'Austria'), (b'AZ', b'Azerbaijan'), (b'BS', b'Bahamas'), (b'BH', b'Bahrain'), (b'BD', b'Bangladesh'), (b'BB', b'Barbados'), (b'BY', b'Belarus'), (b'BE', b'Belgium'), (b'BZ', b'Belize'), (b'BJ', b'Benin'), (b'BM', b'Bermuda'), (b'BT', b'Bhutan'), (b'BO', b'Bolivia'), (b'BA', b'Bosnia and Herzegovina'), (b'BW', b'Botswana'), (b'BV', b'Bouvet Island'), (b'BR', b'Brazil'), (b'IO', b'British Indian Ocean Territory'), (b'BN', b'Brunei Darussalam'), (b'BG', b'Bulgaria'), (b'BF', b'Burkina Faso'), (b'BI', b'Burundi'), (b'KH', b'Cambodia'), (b'CM', b'Cameroon'), (b'CA', b'Canada'), (b'CV', b'Cape Verde'), (b'KY', b'Cayman Islands'), (b'CF', b'Central African Republic'), (b'TD', b'Chad'), (b'CL', b'Chile'), (b'CN', b'China'), (b'CX', b'Christmas Island'), (b'CC', b'Cocos (Keeling) Islands'), (b'CO', b'Colombia'), (b'KM', b'Comoros'), (b'CG', b'Congo'), (b'CD', b'Congo, The Democratic Republic of the'), (b'CK', b'Cook Islands'), (b'CR', b'Costa Rica'), (b'CI', b"Cote D'Ivoire"), (b'HR', b'Croatia'), (b'CU', b'Cuba'), (b'CY', b'Cyprus'), (b'CZ', b'Czech Republic'), (b'DK', b'Denmark'), (b'DJ', b'Djibouti'), (b'DM', b'Dominica'), (b'DO', b'Dominican Republic'), (b'EC', b'Ecuador'), (b'EG', b'Egypt'), (b'SV', b'El Salvador'), (b'GQ', b'Equatorial Guinea'), (b'ER', b'Eritrea'), (b'EE', b'Estonia'), (b'ET', b'Ethiopia'), (b'FK', b'Falkland Islands (Malvinas)'), (b'FO', b'Faroe Islands'), (b'FJ', b'Fiji'), (b'FI', b'Finland'), (b'FR', b'France'), (b'GF', b'French Guiana'), (b'PF', b'French Polynesia'), (b'TF', b'French Southern Territories'), (b'GA', b'Gabon'), (b'GM', b'Gambia'), (b'GE', b'Georgia'), (b'DE', b'Germany'), (b'GH', b'Ghana'), (b'GI', b'Gibraltar'), (b'GR', b'Greece'), (b'GL', b'Greenland'), (b'GD', b'Grenada'), (b'GP', b'Guadeloupe'), (b'GU', b'Guam'), (b'GT', b'Guatemala'), (b'GG', b'Guernsey'), (b'GN', b'Guinea'), (b'GW', b'Guinea-Bissau'), (b'GY', b'Guyana'), (b'HT', b'Haiti'), (b'HM', b'Heard Island and Mcdonald Islands'), (b'VA', b'Holy See (Vatican City State)'), (b'HN', b'Honduras'), (b'HK', b'Hong Kong'), (b'HU', b'Hungary'), (b'IS', b'Iceland'), (b'IN', b'India'), (b'ID', b'Indonesia'), (b'IR', b'Iran, Islamic Republic Of'), (b'IQ', b'Iraq'), (b'IE', b'Ireland'), (b'IM', b'Isle of Man'), (b'IL', b'Israel'), (b'IT', b'Italy'), (b'JM', b'Jamaica'), (b'JP', b'Japan'), (b'JE', b'Jersey'), (b'JO', b'Jordan'), (b'KZ', b'Kazakhstan'), (b'KE', b'Kenya'), (b'KI', b'Kiribati'), (b'KP', b"Korea, Democratic People's Republic of"), (b'KR', b'Korea, Republic of'), (b'KW', b'Kuwait'), (b'KG', b'Kyrgyzstan'), (b'LA', b"Lao People's Democratic Republic"), (b'LV', b'Latvia'), (b'LB', b'Lebanon'), (b'LS', b'Lesotho'), (b'LR', b'Liberia'), (b'LY', b'Libyan Arab Jamahiriya'), (b'LI', b'Liechtenstein'), (b'LT', b'Lithuania'), (b'LU', b'Luxembourg'), (b'MO', b'Macao'), (b'MK', b'Macedonia, The Former Yugoslav Republic of'), (b'MG', b'Madagascar'), (b'MW', b'Malawi'), (b'MY', b'Malaysia'), (b'MV', b'Maldives'), (b'ML', b'Mali'), (b'MT', b'Malta'), (b'MH', b'Marshall Islands'), (b'MQ', b'Martinique'), (b'MR', b'Mauritania'), (b'MU', b'Mauritius'), (b'YT', b'Mayotte'), (b'MX', b'Mexico'), (b'FM', b'Micronesia, Federated States of'), (b'MD', b'Moldova, Republic of'), (b'MC', b'Monaco'), (b'MN', b'Mongolia'), (b'MS', b'Montserrat'), (b'MA', b'Morocco'), (b'MZ', b'Mozambique'), (b'MM', b'Myanmar'), (b'NA', b'Namibia'), (b'NR', b'Nauru'), (b'NP', b'Nepal'), (b'NL', b'Netherlands'), (b'AN', b'Netherlands Antilles'), (b'NC', b'New Caledonia'), (b'NZ', b'New Zealand'), (b'NI', b'Nicaragua'), (b'NE', b'Niger'), (b'NG', b'Nigeria'), (b'NU', b'Niue'), (b'NF', b'Norfolk Island'), (b'MP', b'Northern Mariana Islands'), (b'NO', b'Norway'), (b'OM', b'Oman'), (b'PK', b'Pakistan'), (b'PW', b'Palau'), (b'PS', b'Palestinian Territory, Occupied'), (b'PA', b'Panama'), (b'PG', b'Papua New Guinea'), (b'PY', b'Paraguay'), (b'PE', b'Peru'), (b'PH', b'Philippines'), (b'PN', b'Pitcairn'), (b'PL', b'Poland'), (b'PT', b'Portugal'), (b'PR', b'Puerto Rico'), (b'QA', b'Qatar'), (b'RE', b'Reunion'), (b'RO', b'Romania'), (b'RU', b'Russian Federation'), (b'RW', b'Rwanda'), (b'SH', b'Saint Helena'), (b'KN', b'Saint Kitts and Nevis'), (b'LC', b'Saint Lucia'), (b'PM', b'Saint Pierre and Miquelon'), (b'VC', b'Saint Vincent and the Grenadines'), (b'WS', b'Samoa'), (b'SM', b'San Marino'), (b'ST', b'Sao Tome and Principe'), (b'SA', b'Saudi Arabia'), (b'SN', b'Senegal'), (b'CS', b'Serbia and Montenegro'), (b'SC', b'Seychelles'), (b'SL', b'Sierra Leone'), (b'SG', b'Singapore'), (b'SK', b'Slovakia'), (b'SI', b'Slovenia'), (b'SB', b'Solomon Islands'), (b'SO', b'Somalia'), (b'ZA', b'South Africa'), (b'GS', b'South Georgia and the South Sandwich Islands'), (b'ES', b'Spain'), (b'LK', b'Sri Lanka'), (b'SD', b'Sudan'), (b'SR', b'Suriname'), (b'SJ', b'Svalbard and Jan Mayen'), (b'SZ', b'Swaziland'), (b'SE', b'Sweden'), (b'CH', b'Switzerland'), (b'SY', b'Syrian Arab Republic'), (b'TW', b'Taiwan, Province of China'), (b'TJ', b'Tajikistan'), (b'TZ', b'Tanzania, United Republic of'), (b'TH', b'Thailand'), (b'TL', b'Timor-Leste'), (b'TG', b'Togo'), (b'TK', b'Tokelau'), (b'TO', b'Tonga'), (b'TT', b'Trinidad and Tobago'), (b'TN', b'Tunisia'), (b'TR', b'Turkey'), (b'TM', b'Turkmenistan'), (b'TC', b'Turks and Caicos Islands'), (b'TV', b'Tuvalu'), (b'UG', b'Uganda'), (b'UA', b'Ukraine'), (b'AE', b'United Arab Emirates'), (b'GB', b'United Kingdom'), (b'US', b'United States'), (b'UM', b'United States Minor Outlying Islands'), (b'UY', b'Uruguay'), (b'UZ', b'Uzbekistan'), (b'VU', b'Vanuatu'), (b'VE', b'Venezuela'), (b'VN', b'Viet Nam'), (b'VG', b'Virgin Islands, British'), (b'VI', b'Virgin Islands, U.S.'), (b'WF', b'Wallis and Futuna'), (b'EH', b'Western Sahara'), (b'YE', b'Yemen'), (b'ZM', b'Zambia'), (b'ZW', b'Zimbabwe')])),
                ('state', models.CharField(default=b'initial', max_length=50)),
                ('project_version', models.PositiveIntegerField(default=0)),
                ('ga_profile_id', models.TextField(null=True, blank=True)),
                ('ga_account_id', models.TextField(null=True, blank=True)),
                ('frontend_custom_domain', models.TextField(default=b'', null=True, blank=True)),
                ('cms_custom_domain', models.TextField(default=b'', null=True, blank=True)),
                ('hub_app_id', models.CharField(max_length=32, null=True, blank=True)),
                ('marathon_cpus', models.FloatField(default=0.1)),
                ('marathon_mem', models.FloatField(default=128.0)),
                ('marathon_instances', models.IntegerField(default=1)),
                ('marathon_health_check_path', models.CharField(max_length=255, null=True, blank=True)),
                ('docker_cmd', models.TextField(null=True, blank=True)),
                ('custom_frontend_settings', models.TextField(null=True, blank=True)),
                ('team_id', models.IntegerField(null=True, blank=True)),
            ],
            options={
                'ordering': ('application_type__title', 'country'),
            },
        ),
        migrations.CreateModel(
            name='ProjectRepo',
            fields=[
                ('project', models.OneToOneField(related_name='repo', primary_key=True, serialize=False, to='unicoremc.Project')),
                ('base_url', models.URLField()),
                ('git_url', models.URLField(null=True, blank=True)),
                ('url', models.URLField(null=True, blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='project',
            name='application_type',
            field=models.ForeignKey(blank=True, to='unicoremc.AppType', null=True),
        ),
        migrations.AddField(
            model_name='project',
            name='available_languages',
            field=models.ManyToManyField(to='unicoremc.Localisation', blank=True),
        ),
        migrations.AddField(
            model_name='project',
            name='default_language',
            field=models.ForeignKey(related_name='default_language', blank=True, to='unicoremc.Localisation', null=True),
        ),
        migrations.AddField(
            model_name='project',
            name='organization',
            field=models.ForeignKey(blank=True, to='organizations.Organization', null=True),
        ),
        migrations.AddField(
            model_name='project',
            name='owner',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='project',
            name='external_repos',
            field=models.ManyToManyField(related_name='external_projects', to='unicoremc.ProjectRepo', blank=True),
        ),
    ]
