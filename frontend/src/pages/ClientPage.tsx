type Appointment = {
  id: number
  appointment_date: string
  appointment_time: string
  status: string
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
  onCancelAppointment: (appointmentId: number) => void
}

function ClientPage({
  appointments,
  appointmentsLoading,
  appointmentsError,
  onCancelAppointment,
  onGoHome,
}: ClientPageProps) {
  const activeAppointments = appointments
    .filter(
      (appointment) =>
        appointment.status === 'scheduled' ||
        appointment.status === 'confirmed',
    )
    .sort((a, b) => {
      const dateA =
        `${a.appointment_date}T${a.appointment_time}`
      const dateB =
        `${b.appointment_date}T${b.appointment_time}`

      return dateA.localeCompare(dateB)
    })

  const pastAppointments = appointments
    .filter(
      (appointment) =>
        appointment.status === 'cancelled' ||
        appointment.status === 'completed',
    )
    .sort((a, b) => {
      const dateA =
        `${a.appointment_date}T${a.appointment_time}`
      const dateB =
        `${b.appointment_date}T${b.appointment_time}`

      return dateB.localeCompare(dateA)
    })


  function getStatusLabel(status: string) {
    switch (status) {
      case 'scheduled':
        return 'Agendado'
      case 'confirmed':
        return 'Confirmado'
      case 'completed':
        return 'Concluído'
      case 'cancelled':
        return 'Cancelado'
      default:
        return status
    }
  }

  function renderAppointmentCard(
    appointment: Appointment,
    showCancelButton: boolean,
  ) {
    return (
      <article className="service-card" key={appointment.id}>
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

        <p className="appointment-status-row">
          <strong>Status:</strong>
          <span
            className={`appointment-status appointment-status--${appointment.status}`}
          >
            {getStatusLabel(appointment.status)}
          </span>
        </p>
        {showCancelButton && (
          <button
            type="button"
            onClick={() =>
              void onCancelAppointment(appointment.id)
            }
          >
            Cancelar agendamento
          </button>
        )}
      </article>
    )
  }

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
          <p>Consulte seus próximos horários e seu histórico.</p>
        </div>

        {appointmentsLoading && (
          <p>Carregando seus agendamentos...</p>
        )}

        {appointmentsError && (
          <p role="alert">{appointmentsError}</p>
        )}

        {!appointmentsLoading && !appointmentsError && (
          <>
            <section aria-labelledby="active-appointments-title">
              <div className="section-heading">
                <h3 id="active-appointments-title">
                  Agendamentos ativos
                </h3>
              </div>

              {activeAppointments.length === 0 ? (
                <p>Você não possui agendamentos ativos.</p>
              ) : (
                <div className="services-grid">
                  {activeAppointments.map((appointment) =>
                    renderAppointmentCard(appointment, true),
                  )}
                </div>
              )}
            </section>

            <section aria-labelledby="appointment-history-title">
              <div className="section-heading">
                <h3 id="appointment-history-title">
                  Histórico de agendamentos
                </h3>
              </div>

              {pastAppointments.length === 0 ? (
                <p>Você ainda não possui registros no histórico.</p>
              ) : (
                <div className="services-grid">
                  {pastAppointments.map((appointment) =>
                    renderAppointmentCard(appointment, false),
                  )}
                </div>
              )}
            </section>
          </>
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
