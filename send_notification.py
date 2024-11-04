import config
import db
from models import DeviceData
import mail

db_client = db.DatabaseClient()

dev_owners: list[tuple] = db_client.fetch_all_owners()
for dev_owner_name, dev_owner_email in dev_owners:

    attachment_details: list[tuple] = []
    owner_devices: list[DeviceData] = db_client.fetch_owner_devices(dev_owner_name)
    for device in owner_devices:
        sensor_data = db_client.fetch_records_last_24hours(device.dev_eui)
        if sensor_data:
            pdf_table = mail.plot_report(
                data=[
                        data.__dict__
                        for data in sensor_data
                    ],
                client_name=dev_owner_name,
                client_address='My Address',
                device_name=device.dev_name,
            )
            attachment_details.append((pdf_table, device))
        else:
            print(f'Device {device.dev_eui} has not send any data yet')
            continue
    message = mail.build_email_message(
        to_email=dev_owner_email,
        subject=f'Hourly temperature for {dev_owner_name}',
        message_body='This is an email from Horepa.ro with hourly temperature',
        attachments=attachment_details,
    )
    mail.send_email(to_email=config.ADMIN_EMAIL, message_body=message)
