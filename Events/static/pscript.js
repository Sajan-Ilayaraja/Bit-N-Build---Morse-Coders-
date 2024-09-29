// Function to navigate to respective pages
function navigateTo(page) {
    window.location.href = page;
}

// Function to handle profile photo upload
function uploadPhoto() {
    document.getElementById('fileUpload').click();
}

// Function to preview uploaded photo
function previewPhoto(event) {
    const profilePhoto = document.getElementById('profilePhoto');
    profilePhoto.src = URL.createObjectURL(event.target.files[0]);
}

// Function to delete profile photo
function deletePhoto() {
    const profilePhoto = document.getElementById('profilePhoto');
    profilePhoto.src = 'default-profile.png'; // Set to default profile photo
}

// Function to discard changes
function discardChanges() {
    document.getElementById('userNameInput').value = "Alaa";
    document.getElementById('password').value = "Xh2@epy";
    document.getElementById('mailId').value = "Alaa123@gmail.com";
    document.getElementById('collegeName').value = "ABC college of engineering";
}
