import { useState } from "react";

const initialPlan = { plan_steps: [], motivation_message: "" };

export default function App() {
  const [jobId, setJobId] = useState("1");
  const [jobTitle, setJobTitle] = useState("Yeni İş");
  const [jobDescription, setJobDescription] = useState("Görevin kısa açıklaması");
  const [plan, setPlan] = useState(initialPlan);
  const [feedback, setFeedback] = useState("");
  const [failureReason, setFailureReason] = useState("");
  const [status, setStatus] = useState("Hazır");

  const fetchPlan = async () => {
    setStatus("Plan oluşturuluyor...");
    const response = await fetch(`/jobs/${jobId}/ai-plan`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        job_title: jobTitle,
        job_description: jobDescription,
      }),
    });
    if (!response.ok) {
      setStatus("Plan oluşturulamadı.");
      return;
    }
    const data = await response.json();
    setPlan(data);
    setStatus("Plan hazır.");
  };

  const sendFeedback = async () => {
    setStatus("Geri bildirim gönderiliyor...");
    const response = await fetch(`/jobs/${jobId}/ai-plan/feedback`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        feedback,
        failure_reason: failureReason || null,
      }),
    });
    if (!response.ok) {
      setStatus("Geri bildirim işlenemedi.");
      return;
    }
    const data = await response.json();
    setPlan(data);
    setStatus("Yeni plan oluşturuldu.");
  };

  return (
    <div style={{ fontFamily: "Arial, sans-serif", padding: "2rem", maxWidth: 720 }}>
      <h1>AI Plan Asistanı</h1>
      <p>Durum: {status}</p>

      <section style={{ marginBottom: "1.5rem" }}>
        <h2>İş Bilgileri</h2>
        <label>
          İş ID
          <input
            value={jobId}
            onChange={(event) => setJobId(event.target.value)}
            style={{ display: "block", marginTop: 8, marginBottom: 12, width: "100%" }}
          />
        </label>
        <label>
          Başlık
          <input
            value={jobTitle}
            onChange={(event) => setJobTitle(event.target.value)}
            style={{ display: "block", marginTop: 8, marginBottom: 12, width: "100%" }}
          />
        </label>
        <label>
          Açıklama
          <textarea
            value={jobDescription}
            onChange={(event) => setJobDescription(event.target.value)}
            rows={3}
            style={{ display: "block", marginTop: 8, width: "100%" }}
          />
        </label>
        <button
          onClick={fetchPlan}
          style={{ marginTop: 12, padding: "0.6rem 1.2rem" }}
        >
          AI Plan Oluştur
        </button>
      </section>

      <section style={{ marginBottom: "1.5rem" }}>
        <h2>Plan</h2>
        {plan.plan_steps.length === 0 ? (
          <p>Henüz plan yok.</p>
        ) : (
          <ol>
            {plan.plan_steps.map((step, index) => (
              <li key={`${step.title}-${index}`}>
                <strong>{step.title}</strong> — {step.detail}
              </li>
            ))}
          </ol>
        )}
        {plan.motivation_message ? (
          <p style={{ marginTop: 12, fontWeight: 600 }}>{plan.motivation_message}</p>
        ) : null}
      </section>

      <section>
        <h2>Geri Bildirim</h2>
        <label>
          Ne oldu?
          <textarea
            value={feedback}
            onChange={(event) => setFeedback(event.target.value)}
            rows={3}
            style={{ display: "block", marginTop: 8, marginBottom: 12, width: "100%" }}
          />
        </label>
        <label>
          Yapamadıysan neden?
          <input
            value={failureReason}
            onChange={(event) => setFailureReason(event.target.value)}
            style={{ display: "block", marginTop: 8, marginBottom: 12, width: "100%" }}
          />
        </label>
        <button
          onClick={sendFeedback}
          style={{ padding: "0.6rem 1.2rem" }}
        >
          Geri Bildirimi Gönder
        </button>
      </section>
    </div>
  );
}
