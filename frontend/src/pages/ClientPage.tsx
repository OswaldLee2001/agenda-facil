type Appointment = {
  id: number
  appointment_date: string
  appointment_time: string
  professional: {
    name: string
  }
  service: {
    name: string
  }
}

type ClientPageProps = {
  appointments: Appointment[]
  appointmentsLoading: boolean
  appointmentsError: string | null
  onGoHome: () => void
}

function ClientPage({
  appointments,
  appointmentsLoading,
  appointmentsError,
  onGoHome,
}: ClientPageProps) {
  return (
    <main className="booking-page">
      <header className="site-header">
        <a
          className="brand"
          href="#inicio"
          onClick={(event) => {
            event.preventDefault()
            onGoHome()
          }}
        >
          <span className="brand-icon">A</span>
          <span>Agenda Fácil</span>
        </a>

        <nav aria-label="Navegação principal">
          <a
            href="#inicio"
            onClick={(event) => {
              event.preventDefault()
              onGoHome()
            }}
          >
            Página inicial
          </a>
        </nav>
      </header>

      <section
        id="area-do-cliente"
        className="services-section"
      >
        <div className="section-heading">
          <span className="eyebrow">SUA CONTA</span>
          <h2>Meus agendamentos</h2>
          <p>Consulte os horários que você reservou.</p>
        </div>

        {appointmentsLoading && (
          <p>Carregando seus agendamentos...</p>
        )}

        {appointmentsError && (
          <p role="alert">{appointmentsError}</p>
        )}

        {!appointmentsLoading &&
          !appointmentsError &&
          appointments.length === 0 && (
            <p>Você ainda não possui agendamentos.</p>
          )}

        {!appointmentsLoading &&
          !appointmentsError &&
          appointments.length > 0 && (
            <div className="services-grid">
              {appointments.map((appointment) => (
                <article
                  className="service-card"
                  key={appointment.id}
                >
                  <h3>{appointment.service.name}</h3>

                  <p>
                    <strong>Profissional:</strong>{' '}
                    {appointment.professional.name}
                  </p>

                  <p>
                    <strong>Data:</strong>{' '}
                    {new Date(
                      `${appointment.appointment_date}T12:00:00`,
                    ).toLocaleDateString('pt-BR')}
                  </p>

                  <p>
                    <strong>Horário:</strong>{' '}
                    {appointment.appointment_time.slice(0, 5)}
                  </p>
                </article>
              ))}
            </div>
          )}
      </section>

      <footer className="site-footer">
        <span>Agenda Fácil</span>
        <span>Seu tempo merece organização.</span>
      </footer>
    </main>
  )
}

export default ClientPage
