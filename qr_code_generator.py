import time
import qrcode

# Define the data for multiple people
data_list = [
    {"name": " ", "id": " ", "mob_no": " ", "category": " "},
    
    # Add more data as needed
]

# Loop through the list of data and generate a QR code for each person
for data in data_list:
    name = data["name"]
    id = data["id"]
    mob_no = data["mob_no"]
    category = data["category"]

    # Format the data string
    qr_data = f"{id},{name},{mob_no},{category}"

    # Generate the QR code
    img = qrcode.make(qr_data)

    # Define the output path for each QR code
    output_path = f"H:\\student barcode\\qrcode_{id}.png"  # Unique name based on ID

    # Save the QR code image
    img.save(output_path)

    print(f"QR code saved successfully for {name} at {output_path}")

