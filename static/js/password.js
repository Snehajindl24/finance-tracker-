// This script provides client-side validation for password strength and matching.

function checkPasswordStrength() {
    const password = document.getElementById('password').value;
    const passwordStrength = document.getElementById('password-strength');
    let strength = 'Weak';
    let color = 'red';
    let feedback = '';

    // Define password strength criteria.
    const hasMinLength = password.length >= 8;
    const hasUpper = /[A-Z]/.test(password);
    const hasNumber = /[0-9]/.test(password);
    const hasSpecialChar = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]+/.test(password);

    // Provide feedback based on the criteria met.
    if (hasMinLength && hasUpper && hasNumber && hasSpecialChar) {
        strength = 'Strong';
        color = 'green';
        feedback = 'Password Strength: Strong';
    } else {
        feedback = 'Weak: ';
        if (!hasMinLength) feedback += '8+ characters, ';
        if (!hasUpper) feedback += 'an uppercase letter, ';
        if (!hasNumber) feedback += 'a number, ';
        if (!hasSpecialChar) feedback += 'a special symbol, ';
        // Remove the trailing comma and space.
        feedback = feedback.replace(/,([^,]*)$/, '$1').trim();
    }
    
    // Update the UI with the feedback.
    passwordStrength.textContent = feedback;
    passwordStrength.style.color = color;

    // Also trigger the password match check, as it depends on the password field.
    checkPasswordMatch();
}

function checkPasswordMatch() {
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm-password').value;
    const matchFeedback = document.getElementById('password-match');

    // Check if the passwords match and are not empty.
    if (password === confirmPassword && confirmPassword !== '') {
        matchFeedback.textContent = 'Passwords match!';
        matchFeedback.style.color = 'green';
    } else if (confirmPassword !== '') {
        matchFeedback.textContent = 'Passwords do not match.';
        matchFeedback.style.color = 'red';
    } else {
        matchFeedback.textContent = '';
    }
}

// Attach event listeners to the password fields to run the checks in real-time.
document.addEventListener('DOMContentLoaded', () => {
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirm-password');

    if (passwordInput && confirmPasswordInput) {
        passwordInput.addEventListener('input', checkPasswordStrength);
        confirmPasswordInput.addEventListener('input', checkPasswordMatch);
    }
});
