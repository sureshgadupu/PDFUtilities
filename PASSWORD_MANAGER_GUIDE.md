# Password Manager Guide

## Overview

The PDF Utilities application now includes a password manager feature that allows you to store frequently used PDF passwords with descriptive names, making it easier to unlock password-protected PDFs.

## Features

### 🔑 Password Storage with Names
- Associate each password with a memorable name (e.g., "Work Documents", "Client PDFs", "Personal Files")
- Easily identify and select the right password for your PDFs

### 💾 Save Passwords
- Click the **save button (💾)** in any password field to save a password
- Enter a descriptive name when saving
- Passwords with the same name can be updated

### ▼ Select Saved Passwords
- Click the **dropdown button (▼)** to view and select from saved passwords
- Passwords are displayed with their associated names
- One-click selection fills the password field instantly

### 👁 Password Visibility
- Toggle password visibility using the **eye button (👁/🙈)**
- Helps verify you've selected the correct password

### ⚙️ Manage Passwords
- Access the password manager through the dropdown menu or directly
- **Add New**: Create new password entries
- **Edit Selected**: Modify existing password names or values
- **Remove Selected**: Delete individual passwords
- **Clear All**: Remove all saved passwords at once

## How to Use

### Saving a Password

1. **Enter a password** in any password field in the file table
2. Click the **💾 save button** next to the password field
3. Enter a **descriptive name** (e.g., "Work PDFs", "Tax Documents")
4. Click **Save**

### Using a Saved Password

1. Click the **▼ dropdown button** next to any password field
2. Select the password by its name from the menu
3. The password will be automatically filled in

### Managing Saved Passwords

1. Click the **▼ dropdown button** on any password field
2. Select **"⚙️ Manage Passwords..."** at the bottom of the menu
3. Use the management dialog to:
   - View all saved passwords in a table
   - Add new passwords
   - Edit existing passwords
   - Remove individual passwords
   - Clear all passwords

## Security Considerations

⚠️ **Important Security Information**

- Passwords are stored in **plain text** in a JSON file located at:
  - Windows: `C:\Users\[YourUsername]\.pdf_utilities\saved_passwords.json`
  - macOS/Linux: `~/.pdf_utilities/saved_passwords.json`

- This feature is designed for convenience, not maximum security
- Only store passwords that you're comfortable having in plain text
- Consider the security of your computer and who has access to it

### Best Practices

✅ **Good Use Cases:**
- Frequently accessed work documents with known passwords
- Personal documents on a secure, personal computer
- PDFs that need to be processed in batches

❌ **Avoid For:**
- Highly sensitive documents
- Shared or public computers
- Documents with passwords you don't want stored locally

## Storage Location

Passwords are stored in:
```
~/.pdf_utilities/saved_passwords.json
```

The file format is:
```json
{
  "passwords": {
    "Work Documents": "password123",
    "Client PDFs": "clientPass456",
    "Personal Files": "mySecret789"
  }
}
```

## Tips

1. **Use Descriptive Names**: Choose names that help you remember what each password is for
2. **Regular Cleanup**: Periodically review and remove passwords you no longer need
3. **Backup**: If you want to preserve your passwords, backup the `saved_passwords.json` file
4. **Testing**: Always test a saved password to ensure it works before relying on it

## Troubleshooting

### Password Not Saving
- Ensure you've entered both a name and a password
- Check that you're not using special characters that might cause issues
- Verify the `.pdf_utilities` folder has write permissions

### Can't See Saved Passwords
- Check that the password manager was initialized correctly
- Verify the `saved_passwords.json` file exists in the correct location
- Try restarting the application

### Password Doesn't Work
- Verify the password is correct by showing it (click 👁 button)
- Check for extra spaces or typos
- Re-save the password if needed

## Examples

### Example Workflow 1: Batch Processing Work PDFs
1. Add multiple work PDFs that all use the same password
2. Enter the password in one field
3. Save it as "Work Password"
4. For other files, use the dropdown to select "Work Password"
5. Process all files with one click

### Example Workflow 2: Multiple Password Types
1. Save different passwords with descriptive names:
   - "Q1 Reports" for quarterly reports
   - "HR Documents" for human resources files
   - "Client ABC" for specific client files
2. Easily select the appropriate password for each file type

## Support

For issues or questions about the password manager feature, please refer to the main documentation or contact support.


