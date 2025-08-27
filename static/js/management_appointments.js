const { createApp } = Vue;

createApp({
    delimiters: ['[[', ']]'],

    data() {
        return {
            prevActiveTable: null,
            showCancelModal: false,
            cancelReason: '',
            cancelTargetIndex: null,
            ready: false,
            toasts: [],
            calendar: {
                year: null,
                month: null,
                monthTitle: '',
                weekdays: ['ش', 'ی', 'د', 'س', 'چ', 'پ', 'ج'],
                grid: [],
                markedDates: {},
            },
            selectedDayNum: null,
            selectedDayMonth: null,
            selectedDayYear: null,
            allAppointments: [
                { date: null , time: null , user_fullname: "جواد محمدی", status: 'pending' },
                { date: null , time: null , user_fullname: "یونس محمدی", status: 'pending' },
                { date: null , time: null , user_fullname: "اصغر محمدی", status: 'pending' },
                { date: null , time: null , user_fullname: "اکبر محمدی", status: 'pending' },
                { date: null , time: null , user_fullname: "جواد محمدی", status: 'pending' },
                { date: null , time: null , user_fullname: "یونس محمدی", status: 'pending' },

                { date: '1404/06/03', time: "09:00", user_fullname: "اصغر محمدی", status: 'confirmed' },
                { date: '1404/06/03', time: "09:30", user_fullname: "اکبر محمدی", status: 'confirmed' },

                { date: '1404/06/20', time: '10:00', user_fullname: "جعفر جعفری", status: 'confirmed' },
                { date: null, time: null , user_fullname: "محمد محمدی", status: 'pending' },
                { date: null, time: null , user_fullname: "علی علوی", status: 'cancel', cancel_reason: 'عدم حضور' },
                { date: '1404/06/25', time: '10:30', user_fullname: "رضا رضایی", status: 'confirmed' },
            ],
            draggedIndex: null,
            draggedFrom: null, 
            dragGhostEl: null,
            activeTable: 2,
            selectedDate: null,
            filteredAppointments: [],
            pendingAppointments: [],
            cancelledAppointments: [],
            slotBoxes: [],
            slotCapacity: 3,
        };
    },
    computed: {
        pendingCount() {
            // فقط نوبت‌های با وضعیت 'pending'
            return this.allAppointments.filter(a => a.status === 'pending').length;
        },
        cancelledCount() {
            return this.allAppointments.filter(a => a.status === 'cancel').length;
        },
        underlineColor() {
            switch (this.activeTable) {
                case 1: return '#34d399'; // تایید شده‌ها
                case 2: return '#fbbf24'; // در انتظار بررسی
                case 3: return '#fb7185'; // لغو شده‌ها
                default: return '#34d399';
            }
        },
        monthTitle() {
            const mn = ['فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور', 'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند'];
            return mn[this.calendar.month - 1] || '';
        }
    },

    methods: {
        showToast(message, type = 'info') {
            const id = Date.now()
            this.toasts.push({ id, message, type })

            // پاک کردن بعد از 4 ثانیه
            setTimeout(() => {
                this.toasts = this.toasts.filter(t => t.id !== id)
            }, 4000)
        },
        // ============ Calendar build =============
        initCalendar() {
            const today = new Date();
            const j = jalaali.toJalaali(today.getFullYear(), today.getMonth() + 1, today.getDate());
            this.calendar.year = j.jy;
            this.calendar.month = j.jm;
            this.buildCalendar();
        },

        buildCalendar() {
            const g = jalaali.toGregorian(this.calendar.year, this.calendar.month, 1);
            const first = new Date(g.gy, g.gm - 1, g.gd);
            const monthLength = jalaali.jalaaliMonthLength(this.calendar.year, this.calendar.month);
            // convert JS weekday to our start (شنبه)
            const firstWeekday = (first.getDay() + 1) % 7;
            this.calendar.grid = [];
            for (let i = 0; i < firstWeekday; i++) this.calendar.grid.push({ num: null });
            const today = new Date();
            const todayJ = jalaali.toJalaali(today.getFullYear(), today.getMonth() + 1, today.getDate());
            for (let d = 1; d <= monthLength; d++) {
                const isToday = (this.calendar.year === todayJ.jy && this.calendar.month === todayJ.jm && d === todayJ.jd);
                const g2 = jalaali.toGregorian(this.calendar.year, this.calendar.month, d);
                const isHoliday = new Date(g2.gy, g2.gm - 1, g2.gd).getDay() === 5; // جمعه
                const dateStr = `${this.calendar.year}/${String(this.calendar.month).padStart(2, '0')}/${String(d).padStart(2, '0')}`;
                const eventCount = this.calendar.markedDates[dateStr] || 0;

                // determine past
                let isPast = false;
                if (!isToday) {
                    if (this.calendar.year < todayJ.jy) isPast = true;
                    else if (this.calendar.year === todayJ.jy && this.calendar.month < todayJ.jm) isPast = true;
                    else if (this.calendar.year === todayJ.jy && this.calendar.month === todayJ.jm && d < todayJ.jd) isPast = true;
                }

                this.calendar.grid.push({ num: d, isToday, isHoliday, eventCount, isPast });
            }
            while (this.calendar.grid.length % 7 !== 0) this.calendar.grid.push({ num: null });
        },

        prevMonth() {
            if (this.calendar.month === 1) { this.calendar.month = 12; this.calendar.year--; } else this.calendar.month--;
            this.buildCalendar();
        },

        nextMonth() {
            if (this.calendar.month === 12) { this.calendar.month = 1; this.calendar.year++; } else this.calendar.month++;
            this.buildCalendar();
        },

        selectDay(day) {
            this.selectedDayNum = day;
            this.selectedDayMonth = this.calendar.month;
            this.selectedDayYear = this.calendar.year;
            const dateStr = `${this.calendar.year}/${String(this.calendar.month).padStart(2, '0')}/${String(day).padStart(2, '0')}`;
            this.selectedDate = dateStr;
            this.activeTable = 1;
            this.refreshDerived();
        },

        // ============ Appointments init & derived ============
        initAppointments() {
            const today = new Date();
            const j = jalaali.toJalaali(today.getFullYear(), today.getMonth() + 1, today.getDate());
            this.selectedDate = `${j.jy}/${String(j.jm).padStart(2, '0')}/${String(j.jd).padStart(2, '0')}`;
            this.selectedDayNum = j.jd;
            this.selectedDayMonth = j.jm;
            this.selectedDayYear = j.jy;

            this.slotBoxes = [
                { time: "08:00", items: [] },
                { time: "08:30", items: [] },
                { time: "09:00", items: [] },
                { time: "09:30", items: [] },
                { time: "10:00", items: [] },
                { time: "10:30", items: [] }
            ];

            this.refreshDerived();
            this.emitUpdatedDates();
        },

        statusText(s) { return s === 'confirmed' ? 'تایید شده' : s === 'pending' ? 'در انتظار' : 'لغو شده'; },

        refreshDerived() {
            // set unique _idx
            this.filteredAppointments = this.allAppointments
                .map((a, idx) => ({ ...a, _idx: idx }))
                .filter(a => a.date === this.selectedDate && a.status === 'confirmed');

            this.pendingAppointments = this.allAppointments
                .map((a, idx) => ({ ...a, _idx: idx }))
                .filter(a => a.status === 'pending');

            this.cancelledAppointments = this.allAppointments
                .map((a, idx) => ({ ...a, _idx: idx }))
                .filter(a => a.status === 'cancel');

            // reset slots
            this.slotBoxes.forEach(s => s.items = []);
            // fill slots with confirmed of selectedDate
            this.filteredAppointments.forEach((a) => {
                const slot = this.slotBoxes.find(s => s.time === a.time);
                if (slot) slot.items.push({ ...a });
            });
        },

        emitUpdatedDates() {
            const map = {};
            this.allAppointments.forEach(a => {
                if (a.date && a.status === 'confirmed') {
                    map[a.date] = (map[a.date] || 0) + 1;
                }
            });
            // keep in local calendar state and rebuild grid so dots update
            this.calendar.markedDates = map;
            this.buildCalendar();
            // also dispatch event for backward compatibility (if other code listens)
            window.dispatchEvent(new CustomEvent('appointments-updated', { detail: map }));
        },

        // ============ Slot & Drag logic ============
        assignToLeastPopulatedSlot(dateStr) {
            // dateStr: "yyyy/mm/dd" مقصد — اما ما selectedDate/selectedDay* را تغییر نمی‌دهیم

            // ساخت یک نقشه از زمان->تعداد تایید شده ها برای تاریخ مقصد
            const counts = {};
            for (let s of this.slotBoxes) counts[s.time] = 0;

            this.allAppointments.forEach(a => {
                if (a.date === dateStr && a.status === 'confirmed' && a.time && counts.hasOwnProperty(a.time)) {
                    counts[a.time] = (counts[a.time] || 0) + 1;
                }
            });

            // پیدا کردن اسلاتی با کمترین تعداد که کمتر از ظرفیت باشد
            let chosenIdx = -1;
            let minCount = Infinity;
            for (let i = 0; i < this.slotBoxes.length; i++) {
                const time = this.slotBoxes[i].time;
                const c = counts[time] || 0;
                if (c < minCount && c < this.slotCapacity) {
                    minCount = c;
                    chosenIdx = i;
                }
            }

            // اگر هیچ اسلاتی خالی نبود، در صورت تمایل fallback به اولین اسلات < capacity
            if (chosenIdx === -1) {
                for (let i = 0; i < this.slotBoxes.length; i++) {
                    const time = this.slotBoxes[i].time;
                    const c = counts[time] || 0;
                    if (c < this.slotCapacity) { chosenIdx = i; break; }
                }
            }

            if (chosenIdx === -1) return false;

            if (this.draggedIndex != null && this.allAppointments[this.draggedIndex]) {
                // فقط رکورد را بروزرسانی کن — نمای انتخاب‌شده را تغییر نده
                this.allAppointments[this.draggedIndex].status = 'confirmed';
                this.allAppointments[this.draggedIndex].date = dateStr;
                this.allAppointments[this.draggedIndex].time = this.slotBoxes[chosenIdx].time;

                // اکنون تقویم و نمای اسلات‌های روزِ فعلی را بروزرسانی کن
                this.emitUpdatedDates(); // بروزرسانی dot ها و markedDates
                this.refreshDerived();   // بازسازی slotBoxes برای روزی که الان انتخاب شده (بدون تغییر سلکت)

                return true;
            }
            return false;
        },

        // Drag from pending pool
        dragStart(globalIndex, event) {
            this.draggedIndex = globalIndex;
            this.draggedFrom = { type: 'pool' }; // normalize to object
            this.draggedAppt = this.allAppointments[globalIndex] || null;
            // create drag image
            try {
                if (event.dataTransfer) {
                    event.dataTransfer.setData('text/plain', String(globalIndex));
                    event.dataTransfer.effectAllowed = 'move';
                }
            } catch (err) {
                console.warn('dataTransfer.setData failed', err);
            }
            try {
                const canvas = document.createElement('canvas');
                const size = 24;
                canvas.width = size; canvas.height = size;
                const ctx = canvas.getContext('2d');
                ctx.beginPath();
                ctx.arc(size / 2, size / 2, size / 2 - 1, 0, Math.PI * 2);
                ctx.fillStyle = '#22c55e';
                ctx.fill();
                ctx.lineWidth = 1.2; ctx.strokeStyle = 'rgba(255,255,255,0.9)'; ctx.stroke(); ctx.closePath();
                if (event.dataTransfer && event.dataTransfer.setDragImage) {
                    event.dataTransfer.effectAllowed = 'move';
                    event.dataTransfer.setDragImage(canvas, size / 2, size / 2);
                }
            } catch (err) {
                console.warn('setDragImage failed:', err);
            }
            if (event.target) event.target.classList.add('dragging');
            document.body.classList.add('dragging');
        },

        dragEnd(event) {
            this.draggedIndex = null;
            this.draggedFrom = null;
            this.draggedAppt = null;

            // remove dragging class from any element and body
            try {
                document.querySelectorAll('.dragging').forEach(el => el.classList.remove('dragging'));
            } catch (err) { }
            document.body.classList.remove('dragging');
            this.refreshDerived();
        },

        // touch (mobile) start for pending
        touchStart(globalIndex, e) {
            if (e.cancelable) e.preventDefault();
            this.draggedIndex = globalIndex;
            this.draggedFrom = { type: 'pool' };
            if (!this.dragGhostEl) {
                const g = document.createElement('div');
                g.className = 'drag-ghost';
                document.body.appendChild(g);
                this.dragGhostEl = g;
            }
            const touch = e.touches ? e.touches[0] : e;
            this.dragGhostEl.style.display = 'block';
            this.dragGhostEl.style.left = `${touch.clientX}px`;
            this.dragGhostEl.style.top = `${touch.clientY}px`;

            this._touchMoveHandler = this.touchMove.bind(this);
            this._touchEndHandler = this.touchEnd.bind(this);
            document.addEventListener('touchmove', this._touchMoveHandler, { passive: false });
            document.addEventListener('touchend', this._touchEndHandler, { passive: false });
            document.addEventListener('touchcancel', this._touchEndHandler, { passive: false });

            document.body.classList.add('dragging');
        },

        touchMove(e) {
            if (e.cancelable) e.preventDefault();
            const t = e.touches ? e.touches[0] : e;
            if (this.dragGhostEl) {
                this.dragGhostEl.style.left = `${t.clientX}px`;
                this.dragGhostEl.style.top = `${t.clientY}px`;
            }
        },

        _clearDragState(keepCancelTarget = false) {
            this.draggedIndex = null;
            this.draggedFrom = null;
            this.draggedAppt = null;
            document.body.classList.remove('dragging');
            if (!keepCancelTarget) {
                this.cancelTargetIndex = null;
            }
        },

        touchEnd(e) {
            try {
                document.removeEventListener('touchmove', this._touchMoveHandler);
                document.removeEventListener('touchend', this._touchEndHandler);
                document.removeEventListener('touchcancel', this._touchEndHandler);
            } catch (err) { }

            if (this.dragGhostEl) this.dragGhostEl.style.display = 'none';

            const touch = (e.changedTouches && e.changedTouches[0]) ? e.changedTouches[0] :
                (e.touches && e.touches[0]) || null;
            if (!touch) {
                this._clearDragState();
                return;
            }

            const x = touch.clientX, y = touch.clientY;
            const el = document.elementFromPoint(x, y);
            if (!el) { this._clearDragState(); return; }

            // 1) drop روی تقویم
            const cell = el.closest('[data-day]');
            if (cell && cell.dataset && cell.dataset.day) {
                const day = Number(cell.dataset.day);
                const month = Number(cell.dataset.month);
                const year = Number(cell.dataset.year);
                const dateStr = `${year}/${String(month).padStart(2, '0')}/${String(day).padStart(2, '0')}`;
                if (!this.isDateInPast(dateStr)) {
                    const ok = this.assignToLeastPopulatedSlot(dateStr);
                    if (!ok) this.showToast('برای این روز هیچ اسلات خالی‌ وجود ندارد.', 'warning');
                }
                this._clearDragState();
                return;
            }

            // 2) drop روی تب pending
            const pendingTabEl = el.closest('[data-drop-target="pending"]');
            if (pendingTabEl) {
                // اگر از اسلات میاد، تبدیل به pending کن
                if (this.draggedFrom && this.draggedFrom.type === 'slot' && this.draggedIndex != null) {
                    const gIdx = this.draggedIndex;
                    if (gIdx >= 0 && this.allAppointments[gIdx]) {
                        this.allAppointments[gIdx].status = 'pending';
                        this.allAppointments[gIdx].date = null;
                        this.allAppointments[gIdx].time = null;
                        delete this.allAppointments[gIdx].cancel_reason;
                        this.refreshDerived();
                        this.emitUpdatedDates();
                    }
                }
                this._clearDragState();
                return;
            }

            // 3) drop روی تب cancel (باز کردن modal)
            const cancelTabEl = el.closest('[data-drop-target="cancel"]');
            if (cancelTabEl) {
                let gIdx = this.draggedIndex;
                if ((gIdx == null || gIdx === undefined) && this.draggedAppt) {
                    gIdx = this.allAppointments.findIndex(a => a === this.draggedAppt);
                }
                if (typeof gIdx === 'number' && gIdx >= 0 && this.allAppointments[gIdx]) {
                    this.cancelTargetIndex = gIdx;
                    this.cancelReason = '';
                    this.showCancelModal = true;
                }
                // نگه داشتن cancelTargetIndex تا کاربر modal را تایید یا انصراف دهد
                this._clearDragState(true); // pass keepCancelTarget = true
                return;
            }

            // 4) drop روی slot-box (جابجایی یا تخصیص مستقیم)
            const slotEl = el.closest('.slot-box') || el.closest('[data-slot-index]');
            if (slotEl && slotEl.dataset && slotEl.dataset.slotIndex !== undefined) {
                const targetSi = Number(slotEl.dataset.slotIndex);
                // از pool -> slot
                if (this.draggedFrom && this.draggedFrom.type === 'pool') {
                    const appt = this.pendingAppointments.find(p => p._idx === this.draggedIndex);
                    if (appt) {
                        if (this.slotBoxes[targetSi].items.length >= this.slotCapacity) {
                            this.showToast("این بازه پر شده است!", 'warning');
                        } else {
                            this.allAppointments[appt._idx].status = 'confirmed';
                            this.allAppointments[appt._idx].date = this.selectedDate;
                            this.allAppointments[appt._idx].time = this.slotBoxes[targetSi].time;
                            this.refreshDerived(); this.emitUpdatedDates();
                        }
                    }
                }
                // از اسلات -> اسلات
                if (this.draggedFrom && this.draggedFrom.type === 'slot') {
                    const fromSi = this.draggedFrom.slotIndex;
                    const item = this.slotBoxes[fromSi].items.find(it => it._idx === this.draggedIndex);
                    if (item) {
                        if (this.slotBoxes[targetSi].items.length >= this.slotCapacity) {
                            this.showToast("این بازه پر شده است!", 'warning');
                        } else {
                            const gIdx = this.allAppointments.findIndex(a =>
                                a.date === item.date && a.user_fullname === item.user_fullname && a.time === item.time
                            );
                            if (gIdx >= 0) {
                                this.allAppointments[gIdx].time = this.slotBoxes[targetSi].time;
                            }
                            this.refreshDerived(); this.emitUpdatedDates();
                        }
                    }
                }
                this._clearDragState();
                return;
            }

            // fallback
            this._clearDragState();
        },


        // Drag from slot (rearrange time)
        dragStartFromSlot(slotIndex, localIdx, e) {
            const item = this.slotBoxes[slotIndex] && this.slotBoxes[slotIndex].items[localIdx];
            if (!item) return;
            this.draggedIndex = item._idx;
            this.draggedFrom = { type: 'slot', slotIndex };
            this.draggedAppt = this.allAppointments[item._idx] || null;

            try {
                if (e.dataTransfer) {
                    e.dataTransfer.setData('text/plain', String(item._idx));
                    e.dataTransfer.effectAllowed = 'move';
                }
            } catch (err) {
                console.warn('dataTransfer.setData failed', err);
            }

            // ساخت دایره به عنوان dragImage
            try {
                const canvas = document.createElement('canvas');
                const size = 24;
                canvas.width = size;
                canvas.height = size;
                const ctx = canvas.getContext('2d');
                ctx.beginPath();
                ctx.arc(size / 2, size / 2, size / 2 - 1, 0, Math.PI * 2);
                ctx.fillStyle = '#22c55e'; // رنگ سبز
                ctx.fill();
                ctx.lineWidth = 1.2;
                ctx.strokeStyle = 'rgba(255,255,255,0.9)';
                ctx.stroke();
                ctx.closePath();
                if (e.dataTransfer && e.dataTransfer.setDragImage) {
                    e.dataTransfer.effectAllowed = 'move';
                    e.dataTransfer.setDragImage(canvas, size / 2, size / 2);
                }
            } catch (err) {
                console.warn('setDragImage failed:', err);
            }

            if (e.target) e.target.classList.add('dragging');
            document.body.classList.add('dragging');
        },


        touchStartFromSlot(slotIndex, localIdx, e) {
            if (e.cancelable) e.preventDefault();
            const item = this.slotBoxes[slotIndex] && this.slotBoxes[slotIndex].items[localIdx];
            if (!item) return;
            this.draggedIndex = item._idx;
            this.draggedFrom = { type: 'slot', slotIndex, localIdx };

            if (!this.dragGhostEl) {
                const g = document.createElement('div');
                g.className = 'drag-ghost';
                // optional: show small number inside ghost
                g.textContent = '';
                document.body.appendChild(g);
                this.dragGhostEl = g;
            }
            const touch = e.touches ? e.touches[0] : e;
            this.dragGhostEl.style.display = 'block';
            this.dragGhostEl.style.left = `${touch.clientX}px`;
            this.dragGhostEl.style.top = `${touch.clientY}px`;

            this._touchMoveHandler = this.touchMove.bind(this);
            this._touchEndHandler = this.touchEnd.bind(this);
            document.addEventListener('touchmove', this._touchMoveHandler, { passive: false });
            document.addEventListener('touchend', this._touchEndHandler, { passive: false });
            document.addEventListener('touchcancel', this._touchEndHandler, { passive: false });

            document.body.classList.add('dragging');
        },


        dragEndSlot(e) {
            this.draggedIndex = null;
            this.draggedFrom = null;
            this.draggedAppt = null;
            if (e.target) e.target.classList.remove('dragging');
            document.body.classList.remove('dragging');
        },

        // drop on a slot
        onSlotDragOver(e, si) {
            if (this.isSelectedDatePast()) return;
            if (this.draggedFrom && this.draggedFrom.type === 'slot' && this.draggedFrom.slotIndex === si) return;
            e.preventDefault();
        },

        onSlotDrop(e, si) {
            if (this.isSelectedDatePast()) return;
            if (this.draggedIndex == null) return;

            // if dragged from pending pool
            if (this.draggedFrom && this.draggedFrom.type === 'pool') {
                const appt = this.pendingAppointments.find(p => p._idx === this.draggedIndex);
                if (!appt) return;
                if (this.slotBoxes[si].items.length >= this.slotCapacity) {
                    this.showToast("این بازه پر شده است!", 'warning');
                    return;
                }
                this.allAppointments[appt._idx].status = 'confirmed';
                this.allAppointments[appt._idx].date = this.selectedDate;
                this.allAppointments[appt._idx].time = this.slotBoxes[si].time;
                this.refreshDerived();
                this.emitUpdatedDates();
            }

            // if dragged from another slot
            if (this.draggedFrom && this.draggedFrom.type === 'slot') {
                const fromSi = this.draggedFrom.slotIndex;
                const item = this.slotBoxes[fromSi].items.find(it => it._idx === this.draggedIndex);
                if (!item) return;
                if (this.slotBoxes[si].items.length >= this.slotCapacity) {
                    this.showToast("این بازه پر شده است!", 'warning');
                    return;
                }
                // update main appointments array time
                const gIdx = this.allAppointments.findIndex(a => a.date === item.date && a.user_fullname === item.user_fullname && a.time === item.time);
                if (gIdx >= 0) {
                    this.allAppointments[gIdx].time = this.slotBoxes[si].time;
                }
                this.refreshDerived();
                this.emitUpdatedDates();
            }

            this.draggedIndex = null;
            this.draggedFrom = null;
            document.body.classList.remove('dragging');
        },

        // drop on calendar cell (from pool)
        onCellDrop(cell) {
            if (!cell || !cell.num) return;
            const day = cell.num, month = this.calendar.month, year = this.calendar.year;
            const dateStr = `${year}/${String(month).padStart(2, '0')}/${String(day).padStart(2, '0')}`;
            if (this.isDateInPast(dateStr)) { this.draggedIndex = null; this.draggedFrom = null; return; }
            const ok = this.assignToLeastPopulatedSlot(dateStr);
            if (!ok) this.showToast('برای این روز هیچ اسلات خالی‌ وجود ندارد.', 'warning');
        },

        unassignFromSlot(si, idx) {
            const item = this.slotBoxes[si] && this.slotBoxes[si].items[idx];
            if (!item) return;
            const gIdx = this.allAppointments.findIndex(a =>
                a.date === item.date && a.time === item.time && a.user_fullname === item.user_fullname
            );
            if (gIdx >= 0) {
                this.allAppointments[gIdx].status = 'pending';
                this.allAppointments[gIdx].date = null;
                this.allAppointments[gIdx].time = null;
                this.refreshDerived();
                this.emitUpdatedDates();
                this.activeTable = 2;
            }
        },

        // set pending / cancel from confirmed list
        setPending(localIndex) {
            const item = this.filteredAppointments[localIndex];
            if (!item) return;
            let gIdx = this.allAppointments.findIndex(a => a === item);
            if (gIdx < 0) {
                gIdx = this.allAppointments.findIndex(a =>
                    a.date === item.date && a.time === item.time && a.user_fullname === item.user_fullname
                );
            }
            if (gIdx >= 0) {
                this.allAppointments[gIdx].status = 'pending';
                this.refreshDerived();
                this.emitUpdatedDates();
                this.activeTable = 2;
            }
        },

        setCancel(localIndex) {
            const item = this.filteredAppointments[localIndex];
            if (!item) return;
            let gIdx = this.allAppointments.findIndex(a => a === item);
            if (gIdx < 0) {
                gIdx = this.allAppointments.findIndex(a =>
                    a.date === item.date && a.time === item.time && a.user_fullname === item.user_fullname
                );
            }
            if (gIdx >= 0) {
                this.allAppointments[gIdx].status = 'cancel';
                this.allAppointments[gIdx].cancel_reason = 'متاسفانه نوبت‌ها پر اند...';
                this.refreshDerived();
                this.emitUpdatedDates();
                this.activeTable = 3;
            }
        },

        // helpers
        isDateInPast(dateStr) {
            if (!dateStr) return false;
            const parts = dateStr.split('/');
            const y = Number(parts[0]), m = Number(parts[1]), d = Number(parts[2]);
            const today = new Date();
            const tj = jalaali.toJalaali(today.getFullYear(), today.getMonth() + 1, today.getDate());
            if (y < tj.jy) return true;
            if (y > tj.jy) return false;
            if (m < tj.jm) return true;
            if (m > tj.jm) return false;
            return d < tj.jd;
        },

        isSelectedDatePast() {
            if (!this.selectedDate) return true;
            const parts = this.selectedDate.split('/');
            const jy = Number(parts[0]), jm = Number(parts[1]), jd = Number(parts[2]);
            const g = jalaali.toGregorian(jy, jm, jd);
            const sel = new Date(g.gy, g.gm - 1, g.gd);
            const today = new Date(); today.setHours(0, 0, 0, 0);
            return sel < today;
        },

        // slot drag start (from slot rows) -> we use dragStartFromSlot
        dragStartFromSlotWrapper(si, idx, e) {
            this.dragStartFromSlot(si, idx, e);
        },

        updateTabUnderline() {
            this.$nextTick(() => {
                const tabs = document.querySelector('.tabs');
                const underline = tabs && tabs.querySelector('.tab-underline');
                const active = tabs && tabs.querySelector('.tab.active');
                if (!tabs || !underline || !active) {
                    // اگر یکی وجود نداشت، مخفی/صف کردن underline
                    if (underline) {
                        underline.style.width = '0px';
                    }
                    return;
                }

                const tabsRect = tabs.getBoundingClientRect();
                const rect = active.getBoundingClientRect();

                // محاسبهٔ left نسبت به کانتینر tabs
                const left = Math.round(rect.left - tabsRect.left);
                const width = Math.round(rect.width);

                // یک فاصله داخلی جزئی تا underline کمی کوتاه‌تر شود (اختیاری)
                const shrink = Math.round(width * 0.08); // 8% shrink
                const finalWidth = Math.max(20, width - shrink);
                const finalLeft = left + Math.round((width - finalWidth) / 2);

                underline.style.width = `${finalWidth}px`;
                underline.style.left = `${finalLeft}px`;

                // اگر می‌خواهی افکت pulse هم اضافه کنی:
                underline.classList.remove('pulse');
                void underline.offsetWidth;
                underline.classList.add('pulse');
            });
        },

        onDragStart(appt) {
            this.draggedAppt = appt;
        },

        onDropToPending(event) {
            // اینجا هم از draggedIndex یا draggedAppt استفاده می‌کنیم
            if (this.draggedIndex == null && !this.draggedAppt) return;

            // اگر از اسلات میاد یا از pool — هدف یکیه: تبدیل به pending و پاک کردن date/time
            let gIdx = this.draggedIndex;
            // اطمینان از اینکه اگر draggedAppt داریم اما draggedIndex null بود، index رو پیدا کنیم
            if ((gIdx == null || gIdx === undefined) && this.draggedAppt) {
                gIdx = this.allAppointments.findIndex(a => a === this.draggedAppt);
            }

            if (typeof gIdx === 'number' && gIdx >= 0 && this.allAppointments[gIdx]) {
                this.allAppointments[gIdx].status = 'pending';
                this.allAppointments[gIdx].date = null;
                this.allAppointments[gIdx].time = null;
                // در صورت دلخواه می‌تونی cancel_reason هم حذف/تنظیم کنی
                delete this.allAppointments[gIdx].cancel_reason;

                this.refreshDerived();
                this.emitUpdatedDates();
            }

            // cleanup
            this.draggedIndex = null;
            this.draggedFrom = null;
            this.draggedAppt = null;
            document.body.classList.remove('dragging');
        },

        onDropToCancelled(event) {
            event.preventDefault && event.preventDefault();

            let gIdx = this.draggedIndex;
            if ((gIdx == null || gIdx === undefined) && this.draggedAppt) {
                gIdx = this.allAppointments.findIndex(a => a === this.draggedAppt);
            }

            if (typeof gIdx === 'number' && gIdx >= 0 && this.allAppointments[gIdx]) {
                this.cancelTargetIndex = gIdx;
                this.cancelReason = '';

                // ذخیره تب قبلی و سوئیچ کردن به تب "لغو شده‌ها" برای بازخورد بصری
                this.prevActiveTable = this.activeTable;
                this.activeTable = 3;
                // بعد از تغییر reactive، موقعیت underline را بروزرسانی کن
                this.$nextTick(() => this.updateTabUnderline());

                // باز کردن مودال
                this.showCancelModal = true;
            }

            // cleanup حالت درگ
            document.body.classList.remove('dragging');
        },

        closeCancelModal() {
            this.showCancelModal = false;
            this.cancelReason = '';
            this.cancelTargetIndex = null;

            // اگر قبلاً تب را برای بازخورد تغییر دادیم، آن را بازگردان
            if (typeof this.prevActiveTable === 'number') {
                this.activeTable = this.prevActiveTable;
                this.prevActiveTable = null;
                this.$nextTick(() => this.updateTabUnderline());
            }

            this._clearDragState(); // تمیز کردن state درگ
        },

        confirmCancel() {
            const gIdx = this.cancelTargetIndex;
            if (typeof gIdx === 'number' && gIdx >= 0 && this.allAppointments[gIdx]) {
                this.allAppointments[gIdx].status = 'cancel';
                this.allAppointments[gIdx].cancel_reason = this.cancelReason && this.cancelReason.trim() ? this.cancelReason.trim() : '—';
                this.allAppointments[gIdx].date = null;
                this.allAppointments[gIdx].time = null;
                this.refreshDerived();
                this.emitUpdatedDates();

                // نمایش تب لغو شده‌ها و حرکت underline
                this.activeTable = 3;
                this.$nextTick(() => this.updateTabUnderline());
            }

            this.showCancelModal = false;
            this.cancelReason = '';
            this.cancelTargetIndex = null;
            this.prevActiveTable = null;
            this._clearDragState();
        },

        // --- mouse-based drag (desktop) - قرار بدید داخل methods:
        mouseStart(globalIndex, e) {
            // for pending pool handle
            if (e.cancelable) e.preventDefault();
            this.draggedIndex = globalIndex;
            this.draggedFrom = { type: 'pool' };
            this.draggedAppt = this.allAppointments[globalIndex] || null;

            if (!this.dragGhostEl) {
                const g = document.createElement('div');
                g.className = 'drag-ghost';
                document.body.appendChild(g);
                this.dragGhostEl = g;
            }
            this.dragGhostEl.style.display = 'block';
            this.dragGhostEl.style.left = `${e.clientX}px`;
            this.dragGhostEl.style.top = `${e.clientY}px`;

            this._mouseMoveHandler = this.mouseMove.bind(this);
            this._mouseUpHandler = this.mouseEnd.bind(this);
            document.addEventListener('mousemove', this._mouseMoveHandler, { passive: false });
            document.addEventListener('mouseup', this._mouseUpHandler, { passive: false });

            document.body.classList.add('dragging');
        },
        mouseStartFromSlot(slotIndex, localIdx, e) {
            if (e.cancelable) e.preventDefault();
            const item = this.slotBoxes[slotIndex] && this.slotBoxes[slotIndex].items[localIdx];
            if (!item) return;
            this.draggedIndex = item._idx;
            this.draggedFrom = { type: 'slot', slotIndex, localIdx };
            this.draggedAppt = this.allAppointments[item._idx] || null;

            if (!this.dragGhostEl) {
                const g = document.createElement('div');
                g.className = 'drag-ghost';
                document.body.appendChild(g);
                this.dragGhostEl = g;
            }
            this.dragGhostEl.style.display = 'block';
            this.dragGhostEl.style.left = `${e.clientX}px`;
            this.dragGhostEl.style.top = `${e.clientY}px`;

            this._mouseMoveHandler = this.mouseMove.bind(this);
            this._mouseUpHandler = this.mouseEnd.bind(this);
            document.addEventListener('mousemove', this._mouseMoveHandler, { passive: false });
            document.addEventListener('mouseup', this._mouseUpHandler, { passive: false });

            document.body.classList.add('dragging');
        },
        mouseMove(e) {
            if (e.cancelable) e.preventDefault();
            if (!this.dragGhostEl) return;
            this.dragGhostEl.style.left = `${e.clientX}px`;
            this.dragGhostEl.style.top = `${e.clientY}px`;
        },
        mouseEnd(e) {
            try {
                document.removeEventListener('mousemove', this._mouseMoveHandler);
                document.removeEventListener('mouseup', this._mouseUpHandler);
            } catch (err) { }
            if (this.dragGhostEl) this.dragGhostEl.style.display = 'none';

            const x = e.clientX, y = e.clientY;
            const el = document.elementFromPoint(x, y);
            if (!el) { this._clearDragState(); return; }

            // reuse logic from touchEnd (keeps behavior same)
            const cell = el.closest('[data-day]');
            if (cell && cell.dataset && cell.dataset.day) {
                const day = Number(cell.dataset.day);
                const month = Number(cell.dataset.month);
                const year = Number(cell.dataset.year);
                const dateStr = `${year}/${String(month).padStart(2, '0')}/${String(day).padStart(2, '0')}`;
                if (!this.isDateInPast(dateStr)) {
                    const ok = this.assignToLeastPopulatedSlot(dateStr);
                    if (!ok) this.showToast('برای این روز هیچ اسلات خالی‌ وجود ندارد.', 'warning');
                }
                this._clearDragState();
                return;
            }

            const pendingTabEl = el.closest('[data-drop-target="pending"]');
            if (pendingTabEl) {
                if (this.draggedFrom && this.draggedFrom.type === 'slot' && this.draggedIndex != null) {
                    const gIdx = this.draggedIndex;
                    if (gIdx >= 0 && this.allAppointments[gIdx]) {
                        this.allAppointments[gIdx].status = 'pending';
                        this.allAppointments[gIdx].date = null;
                        this.allAppointments[gIdx].time = null;
                        delete this.allAppointments[gIdx].cancel_reason;
                        this.refreshDerived();
                        this.emitUpdatedDates();
                    }
                }
                this._clearDragState();
                return;
            }

            const cancelTabEl = el.closest('[data-drop-target="cancel"]');
            if (cancelTabEl) {
                let gIdx = this.draggedIndex;
                if ((gIdx == null || gIdx === undefined) && this.draggedAppt) {
                    gIdx = this.allAppointments.findIndex(a => a === this.draggedAppt);
                }
                if (typeof gIdx === 'number' && gIdx >= 0 && this.allAppointments[gIdx]) {
                    this.cancelTargetIndex = gIdx;
                    this.cancelReason = '';
                    this.prevActiveTable = this.activeTable;
                    this.activeTable = 3;
                    this.$nextTick(() => this.updateTabUnderline());
                    this.showCancelModal = true;
                }
                this._clearDragState(true);
                return;
            }

            const slotEl = el.closest('.slot-box') || el.closest('[data-slot-index]');
            if (slotEl && slotEl.dataset && slotEl.dataset.slotIndex !== undefined) {
                const targetSi = Number(slotEl.dataset.slotIndex);
                if (this.draggedFrom && this.draggedFrom.type === 'pool') {
                    const appt = this.pendingAppointments.find(p => p._idx === this.draggedIndex);
                    if (appt) {
                        if (this.slotBoxes[targetSi].items.length >= this.slotCapacity) {
                            this.showToast("این بازه پر شده است!", 'warning');
                        } else {
                            this.allAppointments[appt._idx].status = 'confirmed';
                            this.allAppointments[appt._idx].date = this.selectedDate;
                            this.allAppointments[appt._idx].time = this.slotBoxes[targetSi].time;
                            this.refreshDerived(); this.emitUpdatedDates();
                        }
                    }
                }
                if (this.draggedFrom && this.draggedFrom.type === 'slot') {
                    const fromSi = this.draggedFrom.slotIndex;
                    const item = this.slotBoxes[fromSi].items.find(it => it._idx === this.draggedIndex);
                    if (item) {
                        if (this.slotBoxes[targetSi].items.length >= this.slotCapacity) {
                            this.showToast("این بازه پر شده است!", 'warning');
                        } else {
                            const gIdx = this.allAppointments.findIndex(a =>
                                a.date === item.date && a.user_fullname === item.user_fullname && a.time === item.time
                            );
                            if (gIdx >= 0) {
                                this.allAppointments[gIdx].time = this.slotBoxes[targetSi].time;
                            }
                            this.refreshDerived(); this.emitUpdatedDates();
                        }
                    }
                }
                this._clearDragState();
                return;
            }

            this._clearDragState();
        },



    },
    mounted() {
        // init calendar & appointments
        this.initCalendar();

        this.initAppointments();

        this.updateTabUnderline();

        this._tabResizeHandler = this.updateTabUnderline.bind(this);
        window.addEventListener('resize', this._tabResizeHandler);
        // react to external events for compatibility (not strictly necessary here)
        window.addEventListener('appointments-updated', (ev) => {
            this.calendar.markedDates = ev.detail || {};
            this.buildCalendar();
        });
        this.ready = true;
    },
    beforeUnmount() {
        try { window.removeEventListener('resize', this._tabResizeHandler); } catch (e) { }
        try { if (this.dragGhostEl && this.dragGhostEl.parentNode) this.dragGhostEl.parentNode.removeChild(this.dragGhostEl); } catch (err) { }
        document.body.classList.remove('dragging');
    },
}).mount('#app');