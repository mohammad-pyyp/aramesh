document.addEventListener('alpine:init', () => {
    Alpine.data('formData', () => ({
        step: 1,
        firstName: '',
        lastName: '',
        phoneNumber: '',
        otpCode: '',
        error: '',
        placeholder: 'نام',
        currentIndex: 0,
        typingInterval: null,
        message: null,
        isLoading: false,
        otpSent: false,
        resendCooldown: 0,
        resendTimer: null,

        init() {
            this.setColors('black');
        },

        setColors(color) {
            const colors = {
                black: '#000',
                orange: '#ff9800',
                red: '#f44336',
                green: '#4caf50'
            };

            document.documentElement.style.setProperty('--bg-float-label', colors[color]);
            document.documentElement.style.setProperty('--color-float-input', colors[color]);
        },

        startTyping(text) {
            clearInterval(this.typingInterval);
            this.placeholder = '';
            this.currentIndex = 0;

            this.typingInterval = setInterval(() => {
                if (this.currentIndex < text.length) {
                    this.placeholder += text[this.currentIndex];
                    this.currentIndex++;
                } else {
                    clearInterval(this.typingInterval);
                }
            }, 50);
        },

        onFocus(field) {
            this.setColors('orange');
            this.clearError();

            const messages = {
                firstName: 'نام خود را وارد کنید...',
                lastName: 'نام خانوادگی خود را وارد کنید...',
                phoneNumber: 'شماره تلفن خود را وارد کنید...',
                otpCode: 'کد تایید را وارد کنید...'
            };

            this.startTyping(messages[field]);
        },

        onBlur(field) {
            this.setColors('black');

            const labels = {
                firstName: 'نام',
                lastName: 'نام خانوادگی',
                phoneNumber: 'شماره تلفن',
                otpCode: 'کد تایید'
            };

            this.startTyping(labels[field]);
        },

        clearError() {
            this.error = '';
        },

        validateName(name, fieldName) {
            const persianRegex = /^[\u0626\u0627-\u063A\u0641-\u0642\u0644-\u0648\u0647\u06A9\u06AF\u06BE\u06CC\u067E\u0686\u0698\u06AF\u06CC\u200C\s\-‌]{3,}$/u;

            if (!name.trim()) {
                return `${fieldName} الزامی است.`;
            }

            if (!persianRegex.test(name.trim())) {
                return `${fieldName} باید فقط شامل حروف فارسی و حداقل ۳ حرف باشد.`;
            }

            return '';
        },

        validatePhoneNumber(phone) {
            if (!phone.trim()) {
                return 'شماره تلفن الزامی است.';
            }

            if (!/^09\d{9}$/.test(phone.trim())) {
                return 'شماره تلفن باید 11 رقم باشد و با 09 شروع شود.';
            }

            return '';
        },

        validateOTP(otp) {
            if (!otp.trim()) {
                return 'کد تایید الزامی است.';
            }

            if (!/^\d{4,6}$/.test(otp.trim())) {
                return 'کد تایید باید 4 تا 6 رقم باشد.';
            }

            return '';
        },

        filterDigits() {
            this.phoneNumber = this.phoneNumber
                // تبدیل اعداد عربی به لاتین
                .replace(/[٠-٩]/g, d => String(d.charCodeAt(0) - 1632))
                // تبدیل اعداد فارسی به لاتین
                .replace(/[۰-۹]/g, d => String(d.charCodeAt(0) - 1776))
                // حذف هر چیزی غیر از 0-9
                .replace(/[^0-9]/g, '');
        },

        nextStep() {
            let isValid = false;

            if (this.step === 1) {
                this.error = this.validateName(this.firstName, 'نام');
                if (!this.error) {
                    isValid = true;
                    this.step = 2;
                    this.startTyping('نام خانوادگی');
                }
            } else if (this.step === 2) {
                this.error = this.validateName(this.lastName, 'نام خانوادگی');
                if (!this.error) {
                    isValid = true;
                    this.step = 3;
                    this.startTyping('شماره تلفن');
                }
            }

            if (this.error) {
                this.setColors('red');
                this.startTyping(this.error);
            }
        },

        prevStep() {
            if (this.step > 1) {
                this.step--;
                this.clearError();
                this.setColors('orange');

                const labels = {
                    1: 'نام',
                    2: 'نام خانوادگی',
                    3: 'شماره تلفن'
                };

                this.startTyping(labels[this.step]);
            }
        },

        async sendOTP() {
            this.error = this.validatePhoneNumber(this.phoneNumber);
            const csrfToken = document.querySelector('input[name=csrfmiddlewaretoken]').value;

            if (this.error) {
                this.setColors('red');
                this.startTyping(this.error);
                return;
            }

            this.isLoading = true;
            this.setColors('orange');
            this.startTyping('در حال ارسال کد تایید...');

            try {
                const response = await axios.post('/api/send-otp/', {
                    phone: this.phoneNumber,
                    mode: 'register'
                }, {
                    headers: {
                        'X-CSRFToken': csrfToken,
                    }
                });

                if (response.data.success) {
                    this.setColors('green');
                    this.startTyping('کد تایید ارسال شد');
                    this.otpSent = true;
                    this.step = 4;
                    this.startTyping('کد تایید');
                    this.startResendCooldown();
                } else {
                    this.setColors('red');
                    this.startTyping(response.data.message || 'خطا در ارسال کد تایید');
                }
            } catch (error) {
                console.error('Error sending OTP:', error);
                this.setColors('red');

                if (error.response && error.response.data) {
                    this.startTyping(error.response.data.message || 'خطا در ارسال کد تایید');
                } else {
                    this.startTyping('خطا در ارتباط با سرور');
                }
            } finally {
                this.isLoading = false;
            }
        },

        async verifyOTP() {
            this.error = this.validateOTP(this.otpCode);
            const csrfToken = document.querySelector('input[name=csrfmiddlewaretoken]').value;

            if (this.error) {
                this.setColors('red');
                this.startTyping(this.error);
                return;
            }

            this.isLoading = true;
            this.setColors('orange');
            this.startTyping('در حال تایید کد...');

            try {
                const response = await axios.post('/api/register/', {
                    phone: this.phoneNumber,
                    otp: this.otpCode,
                    first_name: this.firstName,
                    last_name: this.lastName
                }, {
                    headers: {
                        'X-CSRFToken': csrfToken,
                    }
                });

                if (response.data.success) {
                    this.setColors('green');
                    this.startTyping('ثبت نام موفقیت‌آمیز!');

                    // ذخیره توکن‌ها
                    localStorage.setItem('access_token', response.data.data.access);
                    localStorage.setItem('refresh_token', response.data.data.refresh);

                    this.step = 5;
                } else {
                    this.setColors('red');
                    this.startTyping(response.data.message || 'خطا در ثبت نام');
                }
            } catch (error) {
                console.error('Error verifying OTP:', error);
                this.setColors('red');

                if (error.response && error.response.data) {
                    this.startTyping(error.response.data.message || 'خطا در ثبت نام');
                } else {
                    this.startTyping('خطا در ارتباط با سرور');
                }
            } finally {
                this.isLoading = false;
            }
        },

        async resendOTP() {
            if (this.resendCooldown > 0) return;

            const csrfToken = document.querySelector('input[name=csrfmiddlewaretoken]').value;
            this.isLoading = true;

            try {
                const response = await axios.post('/api/send-otp/', {
                    phone: this.phoneNumber,
                    mode: 'register'
                }, {
                    headers: {
                        'X-CSRFToken': csrfToken,
                    }
                });

                if (response.data.success) {
                    this.setColors('green');
                    this.startTyping('کد تایید مجدداً ارسال شد');
                    this.startResendCooldown();
                } else {
                    this.setColors('red');
                    this.startTyping(response.data.message || 'خطا در ارسال مجدد کد تایید');
                }
            } catch (error) {
                console.error('Error resending OTP:', error);
                this.setColors('red');
                this.startTyping('خطا در ارسال مجدد کد تایید');
            } finally {
                this.isLoading = false;
            }
        },

        startResendCooldown() {
            this.resendCooldown = 60; // 60 seconds cooldown
            this.resendTimer = setInterval(() => {
                this.resendCooldown--;
                if (this.resendCooldown <= 0) {
                    clearInterval(this.resendTimer);
                }
            }, 1000);
        },

        goToDashboard() {
            // هدایت به داشبورد
            window.location.href = '/dashboard/';
        }
    }));
});
