/**
 * MediCare Clinic - Main JavaScript
 * Handles: API calls, Booking wizard, UI interactions
 */

const API_BASE = 'http://127.0.0.1:8000/api';

// ── UTILS ────────────────────────────────────────────────────────────────────
const $ = (sel, ctx = document) => ctx.querySelector(sel);
const $$ = (sel, ctx = document) => [...ctx.querySelectorAll(sel)];

function showToast(message, type = 'info') {
  const container = document.getElementById('toastContainer') || createToastContainer();
  const toast = document.createElement('div');
  const icons = { success: '✅', error: '❌', info: 'ℹ️' };
  toast.className = `toast-custom toast-${type}`;
  toast.innerHTML = `<span>${icons[type]}</span> ${message}`;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.animation = 'slideInRight 0.3s ease reverse';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

function createToastContainer() {
  const c = document.createElement('div');
  c.id = 'toastContainer';
  c.className = 'toast-container-custom';
  document.body.appendChild(c);
  return c;
}

async function apiGet(path) {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

async function apiPost(path, data) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
    body: JSON.stringify(data),
  });
  return res.json();
}

function getCookie(name) {
  const val = `; ${document.cookie}`.split(`; ${name}=`);
  return val.length === 2 ? val.pop().split(';').shift() : '';
}

function formatDate(str) {
  return new Date(str + 'T00:00:00').toLocaleDateString('en-SG', {
    weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
  });
}

function animateCounter(el, target) {
  let count = 0;
  const step = Math.ceil(target / 60);
  const timer = setInterval(() => {
    count = Math.min(count + step, target);
    el.textContent = count.toLocaleString();
    if (count >= target) clearInterval(timer);
  }, 20);
}

// ── SCROLL / NAV ─────────────────────────────────────────────────────────────
(function initNav() {
  const nav = document.getElementById('mainNav');
  const scrollBtn = document.getElementById('scrollTop');
  window.addEventListener('scroll', () => {
    const y = window.scrollY;
    nav?.classList.toggle('scrolled', y > 50);
    if (scrollBtn) {
      scrollBtn.classList.toggle('visible', y > 400);
    }
  });
  scrollBtn?.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));

  // Active nav links
  document.querySelectorAll('.nav-scroll').forEach(link => {
    link.addEventListener('click', e => {
      e.preventDefault();
      const target = document.getElementById(link.dataset.target);
      if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      // close mobile menu
      const toggler = document.querySelector('.navbar-toggler');
      const collapse = document.querySelector('.navbar-collapse');
      if (collapse?.classList.contains('show')) toggler?.click();
    });
  });
})();

// ── PAGE LOADER ───────────────────────────────────────────────────────────────
window.addEventListener('load', () => {
  document.querySelector('.page-loader')?.classList.add('hidden');
  setTimeout(() => {
    document.querySelector('.page-loader')?.remove();
    initAnimations();
    loadStats();
    loadDepartments();
    loadDoctors();
    loadTestimonials();
    initCounterAnimation();
  }, 100);
});

// ── FADE ANIMATIONS ───────────────────────────────────────────────────────────
function initAnimations() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('visible'); });
  }, { threshold: 0.12 });
  document.querySelectorAll('.fade-up').forEach(el => observer.observe(el));
}

// ── COUNTER ANIMATION ─────────────────────────────────────────────────────────
function initCounterAnimation() {
  const observer = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.querySelectorAll('[data-count]').forEach(el => {
          animateCounter(el, parseInt(el.dataset.count));
        });
        observer.unobserve(e.target);
      }
    });
  }, { threshold: 0.4 });
  const section = document.querySelector('.stats-section');
  if (section) observer.observe(section);
}

// ── LOAD STATS ────────────────────────────────────────────────────────────────
async function loadStats() {
  try {
    const res = await apiGet('/stats/');
    if (res.success) {
      const s = res.data;
      const el = id => document.querySelector(`[data-stat="${id}"]`);
      if (el('doctors')) el('doctors').dataset.count = s.total_doctors;
      if (el('departments')) el('departments').dataset.count = s.total_departments;
      if (el('patients')) el('patients').dataset.count = s.total_patients;
    }
  } catch (e) {
    console.warn('Stats load skipped (backend not running)');
  }
}

// ── DEPARTMENTS ───────────────────────────────────────────────────────────────
async function loadDepartments() {
  const container = document.getElementById('departmentsGrid');
  if (!container) return;

  const fallback = [
    { id: 1, name: 'Cardiology', description: 'Heart and cardiovascular care.', icon: 'fas fa-heartbeat' },
    { id: 2, name: 'Neurology', description: 'Brain and nervous system treatment.', icon: 'fas fa-brain' },
    { id: 3, name: 'Orthopedics', description: 'Bone and joint care specialists.', icon: 'fas fa-bone' },
    { id: 4, name: 'Pediatrics', description: "Expert children's health care.", icon: 'fas fa-baby' },
    { id: 5, name: 'Oncology', description: 'Advanced cancer treatment.', icon: 'fas fa-ribbon' },
    { id: 6, name: 'Dermatology', description: 'Skin and hair specialists.', icon: 'fas fa-user-md' },
    { id: 7, name: 'Gynecology', description: "Women's reproductive health.", icon: 'fas fa-female' },
    { id: 8, name: 'General Surgery', description: 'Minimally invasive surgery.', icon: 'fas fa-procedures' },
  ];

  let departments = fallback;
  try {
    const res = await apiGet('/departments/');
    if (res.success && res.data.length) departments = res.data;
  } catch (e) {}

  container.innerHTML = departments.map((d, i) => `
    <div class="col-lg-3 col-md-4 col-sm-6 mb-4 fade-up" style="animation-delay:${i * 0.08}s">
      <div class="dept-card" onclick="filterDoctorsByDept(${d.id}, '${d.name}')">
        <div class="dept-icon"><i class="${d.icon || 'fas fa-stethoscope'}"></i></div>
        <h5>${d.name}</h5>
        <p>${d.description}</p>
        <span class="arrow">Book Now <i class="fas fa-arrow-right"></i></span>
      </div>
    </div>
  `).join('');
  
  // Populate booking modal select
  const deptSelect = document.getElementById('bookingDept');
  if (deptSelect) {
    deptSelect.innerHTML = '<option value="">Select Department</option>' +
      departments.map(d => `<option value="${d.id}">${d.name}</option>`).join('');
  }
  initAnimations();
}

// ── DOCTORS ───────────────────────────────────────────────────────────────────
let allDoctors = [];

async function loadDoctors(deptId = '') {
  const container = document.getElementById('doctorsGrid');
  if (!container) return;

  container.innerHTML = `<div class="col-12 text-center py-4"><div class="loader-spinner mx-auto"></div></div>`;

  const fallback = [
    { id: 1, name: 'Sarah Chen', department_name: 'Cardiology', qualification: 'MD, DM Cardiology', specialization: 'Interventional Cardiology', experience_years: 15, consultation_fee: '150.00', rating: '4.9', total_patients: 1250, is_available: true },
    { id: 2, name: 'James Lim', department_name: 'Neurology', qualification: 'MD, DM Neurology', specialization: 'Stroke & Epilepsy', experience_years: 12, consultation_fee: '130.00', rating: '4.8', total_patients: 980, is_available: true },
    { id: 3, name: 'Priya Sharma', department_name: 'Orthopedics', qualification: 'MBBS, MS Ortho', specialization: 'Joint Replacement', experience_years: 10, consultation_fee: '120.00', rating: '4.7', total_patients: 820, is_available: true },
    { id: 4, name: 'Michael Tan', department_name: 'Pediatrics', qualification: 'MBBS, MD Pediatrics', specialization: 'Child Development', experience_years: 8, consultation_fee: '100.00', rating: '4.9', total_patients: 730, is_available: true },
    { id: 5, name: 'Aisha Rahman', department_name: 'Oncology', qualification: 'MD, DM Oncology', specialization: 'Medical Oncology', experience_years: 14, consultation_fee: '200.00', rating: '4.8', total_patients: 640, is_available: true },
    { id: 6, name: 'David Wong', department_name: 'Dermatology', qualification: 'MBBS, MD Dermatology', specialization: 'Cosmetic Dermatology', experience_years: 9, consultation_fee: '110.00', rating: '4.6', total_patients: 590, is_available: true },
  ];

  try {
    const url = deptId ? `/doctors/?department=${deptId}` : '/doctors/';
    const res = await apiGet(url);
    if (res.success && res.data.length) {
      allDoctors = res.data;
    } else {
      allDoctors = fallback;
    }
  } catch (e) {
    allDoctors = fallback;
  }

  renderDoctors(allDoctors);
}

function renderDoctors(doctors) {
  const container = document.getElementById('doctorsGrid');
  if (!container) return;
  if (!doctors.length) {
    container.innerHTML = `<div class="col-12 text-center py-5"><p class="text-muted">No doctors found.</p></div>`;
    return;
  }
  container.innerHTML = doctors.map((d, i) => {
    const initials = d.name.split(' ').map(n => n[0]).join('').slice(0, 2);
    const stars = '★'.repeat(Math.floor(d.rating)) + '☆'.repeat(5 - Math.floor(d.rating));
    return `
      <div class="col-lg-4 col-md-6 mb-4 fade-up" style="animation-delay:${i * 0.1}s">
        <div class="doctor-card">
          <div class="doctor-img-wrap">
            ${d.photo ? `<img src="${d.photo}" alt="Dr. ${d.name}">` : `<div class="doctor-avatar-placeholder">${initials}</div>`}
            <span class="doctor-badge">Available</span>
          </div>
          <div class="doctor-body">
            <div class="doctor-name">Dr. ${d.name}</div>
            <div class="doctor-spec">${d.specialization} • ${d.department_name}</div>
            <div class="doctor-meta">
              <span class="doctor-meta-item"><i class="fas fa-graduation-cap"></i> ${d.qualification}</span>
              <span class="doctor-meta-item"><i class="fas fa-clock"></i> ${d.experience_years} yrs</span>
              <span class="doctor-meta-item rating-stars">${stars}</span>
              <span class="doctor-meta-item"><i class="fas fa-users"></i> ${d.total_patients.toLocaleString()}+</span>
            </div>
            <div class="d-flex align-items-center justify-content-between mt-3">
              <span class="doc-fee">SGD ${d.consultation_fee}</span>
              <button class="btn-primary-custom py-2 px-4" onclick="openBookingWithDoctor(${d.id}, '${d.name}', '${d.department_name}')">
                <i class="fas fa-calendar-plus"></i> Book
              </button>
            </div>
          </div>
        </div>
      </div>`;
  }).join('');
  initAnimations();
}

function filterDoctorsByDept(deptId, deptName) {
  document.getElementById('doctors')?.scrollIntoView({ behavior: 'smooth' });
  setTimeout(() => loadDoctors(deptId), 400);
}

// Doctor search
document.getElementById('doctorSearch')?.addEventListener('input', function () {
  const q = this.value.toLowerCase();
  const filtered = allDoctors.filter(d =>
    d.name.toLowerCase().includes(q) ||
    d.specialization.toLowerCase().includes(q) ||
    d.department_name.toLowerCase().includes(q)
  );
  renderDoctors(filtered);
});

// ── TESTIMONIALS ──────────────────────────────────────────────────────────────
async function loadTestimonials() {
  const container = document.getElementById('testimonialsGrid');
  if (!container) return;

  const fallback = [
    { id: 1, patient_name: 'Amanda Lee', rating: 5, message: 'Excellent service! Doctors are highly professional. Booking was seamless and staff made me feel comfortable throughout.' },
    { id: 2, patient_name: 'Raj Patel', rating: 5, message: 'Dr. Sarah Chen is amazing. She explained my condition clearly. Treatment was effective. Highly recommend MediCare!' },
    { id: 3, patient_name: 'Linda Goh', rating: 5, message: 'The online booking is very convenient. Got SMS and email confirmation instantly. World-class facility!' },
    { id: 4, patient_name: 'Thomas Ng', rating: 4, message: 'Very good experience. Minimal waiting time and thorough doctors. Will definitely return.' },
    { id: 5, patient_name: 'Fatimah Ibrahim', rating: 5, message: 'Best clinic in the area! The pediatric team is wonderful with children. My son felt comfortable.' },
    { id: 6, patient_name: 'Kevin Tan', rating: 5, message: 'Professional, clean and modern facility. The appointment reminder SMS was very helpful!' },
  ];

  let testimonials = fallback;
  try {
    const res = await apiGet('/testimonials/');
    if (res.success && res.data.length) testimonials = res.data;
  } catch (e) {}

  container.innerHTML = testimonials.map((t, i) => {
    const initial = t.patient_name.charAt(0);
    const stars = '★'.repeat(t.rating) + '☆'.repeat(5 - t.rating);
    return `
      <div class="col-lg-4 col-md-6 mb-4 fade-up" style="animation-delay:${i * 0.08}s">
        <div class="testimonial-card h-100">
          <div class="testimonial-stars">${stars}</div>
          <p class="testimonial-text">${t.message}</p>
          <div class="testimonial-author">
            <div class="author-avatar">${initial}</div>
            <div>
              <div class="author-name">${t.patient_name}</div>
              <div class="author-dept">Verified Patient</div>
            </div>
          </div>
        </div>
      </div>`;
  }).join('');
  initAnimations();
}

// ── BOOKING WIZARD ────────────────────────────────────────────────────────────
let bookingData = {};
let currentStep = 1;
const totalSteps = 3;

function openBookingModal() {
  bookingData = {};
  currentStep = 1;
  updateStepUI();
  resetForm();
  const modal = new bootstrap.Modal(document.getElementById('bookingModal'));
  modal.show();
}

function openBookingWithDoctor(docId, docName, deptName) {
  openBookingModal();
  setTimeout(() => {
    const docSelect = document.getElementById('bookingDoctor');
    if (docSelect) {
      docSelect.value = docId;
      bookingData.doctor_id = docId;
      bookingData.doctor_name = docName;
    }
    document.getElementById('bookingDept')?.dispatchEvent(new Event('change'));
  }, 300);
}

function resetForm() {
  document.getElementById('bookingForm')?.reset();
  document.getElementById('timeSlotsContainer').innerHTML = '';
  document.getElementById('slotsLabel').style.display = 'none';
}

function updateStepUI() {
  document.querySelectorAll('.step-content').forEach((s, i) => {
    s.style.display = (i + 1 === currentStep) ? 'block' : 'none';
  });
  document.querySelectorAll('.step').forEach((s, i) => {
    s.classList.remove('active', 'done');
    if (i + 1 === currentStep) s.classList.add('active');
    else if (i + 1 < currentStep) s.classList.add('done');
  });
  document.querySelectorAll('.step-line').forEach((l, i) => {
    l.classList.toggle('done', i < currentStep - 1);
  });
  const prevBtn = document.getElementById('prevBtn');
  const nextBtn = document.getElementById('nextBtn');
  const submitBtn = document.getElementById('submitBtn');
  if (prevBtn) prevBtn.style.display = currentStep > 1 ? 'inline-flex' : 'none';
  if (nextBtn) nextBtn.style.display = currentStep < totalSteps ? 'inline-flex' : 'none';
  if (submitBtn) submitBtn.style.display = currentStep === totalSteps ? 'inline-flex' : 'none';
}

document.getElementById('nextBtn')?.addEventListener('click', async () => {
  if (currentStep === 1 && !validateStep1()) return;
  if (currentStep === 2 && !validateStep2()) return;
  if (currentStep === 2) buildConfirmation();
  currentStep++;
  updateStepUI();
});

document.getElementById('prevBtn')?.addEventListener('click', () => {
  currentStep--;
  updateStepUI();
});

function validateStep1() {
  const dept = document.getElementById('bookingDept').value;
  const doc = document.getElementById('bookingDoctor').value;
  const date = document.getElementById('bookingDate').value;
  const time = document.querySelector('.time-slot.selected')?.dataset.time;

  if (!dept) { showToast('Please select a department', 'error'); return false; }
  if (!doc) { showToast('Please select a doctor', 'error'); return false; }
  if (!date) { showToast('Please select a date', 'error'); return false; }
  if (!time) { showToast('Please select a time slot', 'error'); return false; }

  bookingData.department_id = parseInt(dept);
  bookingData.doctor_id = parseInt(doc);
  bookingData.appointment_date = date;
  bookingData.appointment_time = time;
  bookingData.appointment_type = document.getElementById('bookingType').value;
  return true;
}

function validateStep2() {
  const fields = ['patientFirstName', 'patientLastName', 'patientEmail', 'patientPhone', 'patientGender'];
  for (const id of fields) {
    const el = document.getElementById(id);
    if (!el || !el.value.trim()) {
      showToast(`Please fill in all required fields`, 'error');
      el?.focus();
      return false;
    }
  }
  const email = document.getElementById('patientEmail').value;
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    showToast('Please enter a valid email address', 'error');
    return false;
  }

  bookingData.first_name = document.getElementById('patientFirstName').value;
  bookingData.last_name = document.getElementById('patientLastName').value;
  bookingData.email = email;
  bookingData.phone = document.getElementById('patientPhone').value;
  bookingData.gender = document.getElementById('patientGender').value;
  bookingData.date_of_birth = document.getElementById('patientDOB').value || null;
  bookingData.address = document.getElementById('patientAddress').value;
  bookingData.city = document.getElementById('patientCity').value;
  bookingData.blood_group = document.getElementById('patientBloodGroup').value;
  bookingData.symptoms = document.getElementById('patientSymptoms').value;
  return true;
}

function buildConfirmation() {
  const doctor = allDoctors.find(d => d.id === bookingData.doctor_id);
  const d = bookingData;
  document.getElementById('confirmDetails').innerHTML = `
    <div class="row g-3">
      <div class="col-6">
        <div class="p-3 bg-light rounded-3">
          <div class="text-muted small mb-1">Patient Name</div>
          <strong>${d.first_name} ${d.last_name}</strong>
        </div>
      </div>
      <div class="col-6">
        <div class="p-3 bg-light rounded-3">
          <div class="text-muted small mb-1">Email</div>
          <strong>${d.email}</strong>
        </div>
      </div>
      <div class="col-6">
        <div class="p-3 bg-light rounded-3">
          <div class="text-muted small mb-1">Phone</div>
          <strong>${d.phone}</strong>
        </div>
      </div>
      <div class="col-6">
        <div class="p-3 bg-light rounded-3">
          <div class="text-muted small mb-1">Doctor</div>
          <strong>Dr. ${doctor ? doctor.name : 'Selected Doctor'}</strong>
        </div>
      </div>
      <div class="col-6">
        <div class="p-3 bg-light rounded-3">
          <div class="text-muted small mb-1">Date</div>
          <strong>${formatDate(d.appointment_date)}</strong>
        </div>
      </div>
      <div class="col-6">
        <div class="p-3 bg-light rounded-3">
          <div class="text-muted small mb-1">Time</div>
          <strong>${document.querySelector('.time-slot.selected')?.textContent.trim() || d.appointment_time}</strong>
        </div>
      </div>
      ${d.symptoms ? `<div class="col-12"><div class="p-3 bg-light rounded-3"><div class="text-muted small mb-1">Symptoms</div><strong>${d.symptoms}</strong></div></div>` : ''}
    </div>
  `;
}

document.getElementById('submitBtn')?.addEventListener('click', async () => {
  const btn = document.getElementById('submitBtn');
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span> Booking...';

  try {
    const res = await apiPost('/appointments/book/', bookingData);
    if (res.success) {
      showBookingSuccess(res.data);
    } else {
      const errorMsg = res.message || Object.values(res.errors || {}).flat().join(', ');
      showToast(errorMsg, 'error');
      btn.disabled = false;
      btn.innerHTML = '<i class="fas fa-check me-2"></i> Confirm Booking';
    }
  } catch (e) {
    // Show demo success when backend not connected
    showBookingSuccess({
      reference: 'APT-' + Math.random().toString(36).slice(2, 10).toUpperCase(),
      patient_name: `${bookingData.first_name} ${bookingData.last_name}`,
      doctor: `Dr. ${allDoctors.find(d => d.id === bookingData.doctor_id)?.name || 'Selected'}`,
      date: formatDate(bookingData.appointment_date),
      time: document.querySelector('.time-slot.selected')?.textContent.trim(),
      email_sent: false,
      sms_sent: false,
    });
  }
});

function showBookingSuccess(data) {
  document.querySelectorAll('.step-content').forEach(s => s.style.display = 'none');
  document.getElementById('bookingSuccess').style.display = 'block';
  document.querySelectorAll('#prevBtn, #nextBtn, #submitBtn').forEach(b => b.style.display = 'none');
  document.getElementById('bookingSuccess').innerHTML = `
    <div class="booking-success">
      <div class="success-icon">✅</div>
      <h4 class="text-success mb-2">Appointment Confirmed!</h4>
      <p class="text-muted mb-3">Your appointment has been successfully booked.</p>
      <div class="ref-badge">${data.reference}</div>
      <div class="mt-4 text-start">
        <div class="row g-2">
          <div class="col-6"><div class="p-3 bg-light rounded-3"><small class="text-muted d-block">Patient</small><strong>${data.patient_name}</strong></div></div>
          <div class="col-6"><div class="p-3 bg-light rounded-3"><small class="text-muted d-block">Doctor</small><strong>${data.doctor}</strong></div></div>
          <div class="col-6"><div class="p-3 bg-light rounded-3"><small class="text-muted d-block">Date</small><strong>${data.date}</strong></div></div>
          <div class="col-6"><div class="p-3 bg-light rounded-3"><small class="text-muted d-block">Time</small><strong>${data.time}</strong></div></div>
        </div>
      </div>
      ${data.email_sent ? '<p class="mt-3 text-success small"><i class="fas fa-envelope me-1"></i> Confirmation email sent!</p>' : ''}
      ${data.sms_sent ? '<p class="text-success small"><i class="fas fa-sms me-1"></i> SMS confirmation sent!</p>' : ''}
      <div class="alert alert-info mt-3 text-start" style="font-size:13px;">
        <i class="fas fa-info-circle me-2"></i>
        Please save your reference number and arrive <strong>15 minutes early</strong> on your appointment day.
      </div>
      <button class="btn-primary-custom mt-3" onclick="bootstrap.Modal.getInstance(document.getElementById('bookingModal')).hide()">
        <i class="fas fa-times me-2"></i> Close
      </button>
    </div>`;
  showToast('Appointment booked successfully!', 'success');
}

// ── DEPARTMENT → DOCTOR FILTER ────────────────────────────────────────────────
document.getElementById('bookingDept')?.addEventListener('change', async function () {
  const deptId = this.value;
  const docSelect = document.getElementById('bookingDoctor');
  docSelect.innerHTML = '<option value="">Loading doctors...</option>';

  try {
    const url = deptId ? `/doctors/?department=${deptId}` : '/doctors/';
    const res = await apiGet(url);
    const doctors = res.success ? res.data : allDoctors;
    docSelect.innerHTML = '<option value="">Select Doctor</option>' +
      doctors.map(d => `<option value="${d.id}">Dr. ${d.name} — ${d.specialization}</option>`).join('');
  } catch {
    docSelect.innerHTML = '<option value="">Select Doctor</option>' +
      allDoctors.map(d => `<option value="${d.id}">Dr. ${d.name} — ${d.specialization}</option>`).join('');
  }
});

// ── TIME SLOT LOADER ───────────────────────────────────────────────────────────
async function loadTimeSlots() {
  const docId = document.getElementById('bookingDoctor')?.value;
  const date = document.getElementById('bookingDate')?.value;
  if (!docId || !date) return;

  const container = document.getElementById('timeSlotsContainer');
  const label = document.getElementById('slotsLabel');
  label.style.display = 'block';
  container.innerHTML = `<div class="text-center py-3"><div class="loader-spinner mx-auto"></div></div>`;

  try {
    const res = await apiGet(`/doctors/${docId}/slots/?date=${date}`);
    if (res.success) {
      renderTimeSlots(res.data);
    }
  } catch {
    // Demo slots
    const demoSlots = ['09:00','09:30','10:00','10:30','11:00','11:30','14:00','14:30','15:00','15:30','16:00','16:30']
      .map(t => ({ time: t, display: new Date('2000-01-01T' + t).toLocaleTimeString('en', { hour: 'numeric', minute: '2-digit' }), available: Math.random() > 0.3 }));
    renderTimeSlots(demoSlots);
  }
}

function renderTimeSlots(slots) {
  const container = document.getElementById('timeSlotsContainer');
  if (!slots.length) {
    container.innerHTML = `<p class="text-muted small">No slots available for this date.</p>`;
    return;
  }
  container.innerHTML = `<div class="time-slot-grid">${slots.map(s => `
    <div class="time-slot ${!s.available ? 'booked' : ''}" data-time="${s.time}" ${s.available ? 'onclick="selectSlot(this)"' : ''}>
      ${s.display}
    </div>`).join('')}</div>`;
}

function selectSlot(el) {
  document.querySelectorAll('.time-slot').forEach(s => s.classList.remove('selected'));
  el.classList.add('selected');
}

document.getElementById('bookingDoctor')?.addEventListener('change', loadTimeSlots);
document.getElementById('bookingDate')?.addEventListener('change', loadTimeSlots);

// Set min date for booking
document.addEventListener('DOMContentLoaded', () => {
  const dateInput = document.getElementById('bookingDate');
  if (dateInput) {
    const today = new Date();
    today.setDate(today.getDate() + 1);
    dateInput.min = today.toISOString().split('T')[0];
  }
});

// ── CONTACT FORM ──────────────────────────────────────────────────────────────
document.getElementById('contactForm')?.addEventListener('submit', async function (e) {
  e.preventDefault();
  const btn = this.querySelector('[type=submit]');
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span> Sending...';

  const data = {
    name: document.getElementById('contactName').value,
    email: document.getElementById('contactEmail').value,
    phone: document.getElementById('contactPhone').value || '',
    subject: document.getElementById('contactSubject').value,
    message: document.getElementById('contactMessage').value,
  };

  try {
    const res = await apiPost('/contact/', data);
    if (res.success) {
      showToast(res.message, 'success');
      this.reset();
    } else {
      showToast('Failed to send message. Please try again.', 'error');
    }
  } catch {
    showToast('Message sent! (Demo mode — backend not connected)', 'info');
    this.reset();
  }

  btn.disabled = false;
  btn.innerHTML = '<i class="fas fa-paper-plane me-2"></i> Send Message';
});

// ── CHECK APPOINTMENT ─────────────────────────────────────────────────────────
document.getElementById('checkApptForm')?.addEventListener('submit', async function (e) {
  e.preventDefault();
  const email = document.getElementById('checkApptEmail').value;
  const resultDiv = document.getElementById('checkApptResult');
  resultDiv.innerHTML = `<div class="text-center py-3"><div class="loader-spinner mx-auto"></div></div>`;

  try {
    const res = await apiGet(`/appointments/patient/?email=${encodeURIComponent(email)}`);
    if (res.success) {
      const apts = res.data;
      if (!apts.length) {
        resultDiv.innerHTML = `<p class="text-muted text-center">No appointments found for this email.</p>`;
        return;
      }
      resultDiv.innerHTML = apts.map(a => `
        <div class="p-3 border rounded-3 mb-2">
          <div class="d-flex justify-content-between align-items-start">
            <div>
              <strong>APT-${a.appointment_id.slice(0,8).toUpperCase()}</strong>
              <div class="text-muted small">Dr. ${a.doctor_name} • ${a.department_name}</div>
              <div class="text-muted small">${a.appointment_date} at ${a.appointment_time}</div>
            </div>
            <span class="badge bg-${a.status==='CONFIRMED'?'success':a.status==='CANCELLED'?'danger':'warning'}">${a.status}</span>
          </div>
        </div>`).join('');
    } else {
      resultDiv.innerHTML = `<p class="text-danger text-center">${res.message}</p>`;
    }
  } catch {
    resultDiv.innerHTML = `<p class="text-muted text-center">Backend not connected. Please run Django server.</p>`;
  }
});
