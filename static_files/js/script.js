document.addEventListener('alpine:init', () => {
    Alpine.data('formData', () => ({
        step: 1,
        firstName: '',
        lastName: '',
        phoneNumber: '',
        abjad: "666",
        error: '',
        placeholder: 'نام',
        currentIndex: 0,
        typingInterval: null,
        message: null,


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
                phoneNumber: 'شماره تلفن خود را وارد کنید...'
            };

            this.startTyping(messages[field]);
        },

        onBlur(field) {
            this.setColors('black');

            const labels = {
                firstName: 'نام',
                lastName: 'نام خانوادگی',
                phoneNumber: 'شماره تلفن'
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
                    2: 'نام خانوادگی'
                };

                this.startTyping(labels[this.step]);
            }
        },


        submitForm() {
            this.error = this.validatePhoneNumber(this.phoneNumber);
            const csrfToken = document.querySelector('input[name=csrfmiddlewaretoken]').value;

            if (this.error) {
                this.setColors('red');
                this.startTyping(this.error);
                return;
            }

            axios.post('/api/submit_reserve_form/', {
                firstName: this.firstName,
                lastName: this.lastName,
                phoneNumber: this.phoneNumber
            }, {
                headers: {
                    'X-CSRFToken': csrfToken,
                }
            })
                .then(res => {
                    const data = res.data;
                    if (data.status === 'ok') {
                        this.setColors('green');
                        this.abjad = data.abjad;
                        this.step = 4;
                    } else {
                        console.error(data.error);
                    }
                })
                .catch(err => {
                    console.error('Axios error:', err);
                });

        },

    }));

});
