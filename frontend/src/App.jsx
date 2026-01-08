import { useState } from "react";

const API_BASE = "http://localhost:8000";

export default function App() {
  const [user, setUser] = useState(null);
  const [jobs, setJobs] = useState([]);
  const [plan, setPlan] = useState(null);
  const [note, setNote] = useState("");
  const [status, setStatus] = useState("");

  async function createDemoUser() {
    setStatus("Kullanıcı oluşturuluyor...");
    const response = await fetch(`${API_BASE}/users`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        email: "demo@sanalboss.io",
        name: "Demo Kullanıcı",
      }),
    });

    if (!response.ok) {
      setStatus("Kullanıcı zaten var, listeler yükleniyor.");
    }

    const userResponse = response.ok
      ? response
      : await fetch(`${API_BASE}/users`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            email: `demo-${Date.now()}@sanalboss.io`,
            name: "Yeni Demo Kullanıcı",
          }),
        });

    const userData = await userResponse.json();
    setUser(userData);
    await loadJobs(userData.id);
    setStatus("Kullanıcı hazır.");
  }

  async function loadJobs(userId) {
    const response = await fetch(`${API_BASE}/users/${userId}/jobs`);
    const data = await response.json();
    setJobs(data);
  }

  async function createJob(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const response = await fetch(`${API_BASE}/users/${user.id}/jobs`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        title: formData.get("title"),
        description: formData.get("description"),
      }),
    });
    const job = await response.json();
    setJobs((prev) => [...prev, job]);
    event.target.reset();
  }

  async function addNote(jobId) {
    if (!note) return;
    await fetch(`${API_BASE}/jobs/${jobId}/notes`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ note }),
    });
    setNote("");
    setStatus("Not kaydedildi. Yeni plan için tekrar oluştur.");
  }

  async function generatePlan(jobId) {
    const response = await fetch(`${API_BASE}/jobs/${jobId}/plan`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ start_hour: 12, end_hour: 19, focus_hours: 6 }),
    });
    const data = await response.json();
    setPlan(data);
  }

  return (
    <div className="app">
      <header>
        <div>
          <p className="eyebrow">Sanal Boss • Freelancer çalışma asistanı</p>
          <h1>Zaman planı, hatırlatmalar ve motivasyon tek panelde.</h1>
          <p className="subtitle">
            İşlerini ekle, yapay zeka notlarını parçalayıp saatlik plan
            oluştursun. Yapamadığın işlerde nedenini yaz, Sanal Boss sana
            yönlendirme ve motivasyon versin.
          </p>
        </div>
        <button onClick={createDemoUser} className="primary">
          Demo Kullanıcı Oluştur
        </button>
      </header>

      <section className="panel">
        <h2>Bugünkü İşlerin</h2>
        {!user && <p>İlk adım olarak demo kullanıcıyı oluştur.</p>}
        {user && (
          <form onSubmit={createJob} className="job-form">
            <input name="title" placeholder="İş başlığı" required />
            <textarea
              name="description"
              placeholder="Bu işte neler yapılmalı?"
              required
            />
            <button type="submit">İşi Kaydet</button>
          </form>
        )}
        <div className="grid">
          {jobs.map((job) => (
            <article key={job.id}>
              <h3>{job.title}</h3>
              <p>{job.description}</p>
              <div className="actions">
                <button onClick={() => generatePlan(job.id)}>
                  Plan Oluştur
                </button>
                <button className="ghost" onClick={() => addNote(job.id)}>
                  Notu Kaydet
                </button>
              </div>
            </article>
          ))}
        </div>
      </section>

      <section className="panel note-panel">
        <h2>Günlük Not & Geri Bildirim</h2>
        <textarea
          value={note}
          onChange={(event) => setNote(event.target.value)}
          placeholder="İşi yapamadıysan nedenini yaz, Sanal Boss motivasyon versin."
        />
        {status && <p className="status">{status}</p>}
      </section>

      {plan && (
        <section className="panel plan">
          <h2>Plan Önerisi</h2>
          <p>{plan.message}</p>
          <ul>
            {plan.plan.map((item) => (
              <li key={`${item.start_time}-${item.task}`}>
                <strong>
                  {item.start_time} - {item.end_time}
                </strong>
                <span>{item.task}</span>
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}
