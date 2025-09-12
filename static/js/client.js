// static\js\client.js
class SessionClient {
    constructor() {
        this.api = axios.create({
            baseURL: "/api",           // ← مهم: نسبی، از همان origin استفاده می‌شود
            withCredentials: true,
            headers: { "Content-Type": "application/json" },
            xsrfCookieName: "csrftoken",
            xsrfHeaderName: "X-CSRFToken",
        });
    }

    // --- OTP ---
    async sendOTP(phone, mode = "register") {
        const { data } = await this.api.post("/send-otp/", { phone });
        return data;
    }

    // --- ثبت‌نام ---
    async register(firstName = "", lastName = "", phone, otp) {
        const { data } = await this.api.post("/register/", {
            first_name: firstName,
            last_name: lastName,
            phone,
            otp,
        });
        // می‌تونی user رو تو localStorage ذخیره کنی (بدون توکن)
        localStorage.setItem("user", JSON.stringify(data.data.user));
        return data;
    }

    // --- ورود ---
    async login(phone, otp) {
        const { data } = await this.api.post("/login/", { phone, otp });
        localStorage.setItem("user", JSON.stringify(data.data.user));
        return data;
    }

    // --- خروج ---
    async logout() {
        await this.api.post("/logout/");
        localStorage.removeItem("user");
    }

    // --- پروفایل ---
    async getProfile() {
        const { data } = await this.api.get("/dashboard/");
        return data;
    }

    async updateProfile(profileData) {
        const { data } = await this.api.patch("/profile/", profileData);
        localStorage.setItem("user", JSON.stringify(data.data));
        return data;
    }

    // --- مدیریت User در فرانت ---
    getUser() {
        const user = localStorage.getItem("user");
        return user ? JSON.parse(user) : null;
    }

    clearUser() {
        localStorage.removeItem("user");
    }
}

const sessionClient = new SessionClient();

