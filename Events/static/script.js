// Function to navigate to the profile page
function navigateToProfile() {
    window.location.href = "profile.html"; // Change this URL to the profile page URL
}

// Function to navigate to the second page of the form
function goToPage2() {
    document.getElementById("page1").style.display = "none";
    document.getElementById("page2").style.display = "block";
}

function goToPage3() {
    document.getElementById("page2").style.display = "none";
    document.getElementById("page3").style.display = "block";
}

document.querySelector('form#agreementForm').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent actual form submission
    
    // Display the modal
    document.getElementById("confirmationModal").style.display = "block";
});

// Close the modal when OK button is clicked
document.getElementById("closeModal").addEventListener("click", function() {
    document.getElementById("confirmationModal").style.display = "none";
    
    // Optionally, reset the form after confirmation
    document.getElementById("agreementForm").reset();
});
