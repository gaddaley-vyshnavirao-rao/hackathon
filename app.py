from pathlib import Path
from pathlib import Path
import math
import tempfile, streamlit as st
import networkx as nx
from iaia.project_manager import ProjectManager, UnsafeArchiveError
from iaia.orchestrator import AnalysisOrchestrator
from iaia.analyzers.blast_radius import BlastRadiusAnalyzer
from iaia.reporting.report_generator import ReportGenerator
from iaia.reporting.pdf_generator import PDFReportGenerator
from iaia.ui_helpers import build_dependency_graph
from iaia.intelligence.architecture_copilot import ArchitectureCopilot, QUESTIONS
from iaia.visualization import build_modernization_roadmap

st.set_page_config(page_title='IAIA', layout='wide')
st.markdown('''<style>
:root{--jet:#0A0A0A;--carbon:#121212;--surface:#191919;--blue:#007BA7;--electric:#00BFFF;--rose:#FF4FA3;--red:#E63946;--text:#F3F7FA;--muted:#9AA8B2}
html,body,[data-testid="stAppViewContainer"],[data-testid="stHeader"]{background:var(--jet);color:var(--text)}
[data-testid="stAppViewContainer"]{background:radial-gradient(circle at 90% 0%,rgba(0,123,167,.14),transparent 28rem),var(--jet)}
[data-testid="stHeader"]{background:rgba(10,10,10,.85)}
[data-testid="stSidebar"]{background:var(--carbon);border-right:1px solid rgba(0,191,255,.22)}
h1,h2,h3,h4{color:var(--text);letter-spacing:-.02em} p,li,label,[data-testid="stCaptionContainer"]{color:var(--muted)}
[data-testid="stMetric"]{background:linear-gradient(145deg,#202020,#121212);border:1px solid rgba(0,191,255,.25);border-left:3px solid var(--blue);border-radius:12px;padding:1rem;min-width:0;overflow:visible}
[data-testid="stMetricLabel"]{color:var(--muted);white-space:normal;overflow:visible;text-transform:uppercase;letter-spacing:.08em;font-size:.7rem}[data-testid="stMetricValue"]{color:var(--electric);white-space:normal;overflow-wrap:anywhere;font-size:clamp(1rem,2vw,1.7rem)}
[data-testid="stExpander"]{background:var(--carbon);border:1px solid rgba(0,191,255,.22);border-radius:12px}[data-testid="stAlert"]{background:var(--carbon);border-radius:10px}
[data-baseweb="tab-list"]{border-bottom:1px solid rgba(0,191,255,.2)}[data-baseweb="tab"]{color:var(--muted)}[aria-selected="true"]{color:var(--electric)!important;border-bottom-color:var(--electric)!important}
[data-testid="stFileUploader"]{background:var(--carbon);border:1px dashed rgba(0,191,255,.4);border-radius:10px}input,textarea,[data-baseweb="select"]>div{background:var(--surface)!important;color:var(--text)!important;border-color:rgba(0,191,255,.3)!important}
button[kind="primary"]{background:linear-gradient(135deg,var(--blue),var(--electric));border:0;color:white;font-weight:700}button[kind="primary"]:hover{background:linear-gradient(135deg,var(--blue),var(--rose))}
[data-testid="stDownloadButton"] button{background:#202020;color:var(--electric);border-color:rgba(0,191,255,.35)}[data-testid="stPlotlyChart"]{background:var(--carbon);border:1px solid rgba(0,191,255,.22);border-radius:12px}code{color:#79DFFF;background:rgba(0,123,167,.15)}
.iaia-ai{background:linear-gradient(145deg,rgba(255,79,163,.16),#121212);border:1px solid var(--rose);border-left:4px solid var(--rose);border-radius:12px;padding:1rem;margin:.7rem 0}.iaia-ai strong{color:var(--rose)}
.security-card{background:#121212;border:1px solid #E63946;border-left:4px solid #E63946;border-radius:12px;padding:1rem;margin:.7rem 0}.security-card h3{color:#F3F7FA}.security-card strong{color:#F3F7FA}.security-meta{color:#9AA8B2}.badge{display:inline-block;border-radius:999px;padding:.2rem .6rem;font-size:.72rem;font-weight:800;text-transform:uppercase}.critical{color:#E63946;border:1px solid #E63946;background:#E6394622}.high{color:#FF4FA3;border:1px solid #FF4FA3;background:#FF4FA322}.medium{color:#E63946;border:1px solid #E63946;background:#E6394622}.low{color:#007BA7;border:1px solid #007BA7;background:#007BA722}
</style>''',unsafe_allow_html=True)
st.title('IAIA - Industrial Architecture Intelligence Agent')
st.caption('Static-analysis prototype. Findings and graph impact require engineering validation.')
if 'source' not in st.session_state:
    st.session_state.source=None
if 'result' not in st.session_state:
    st.session_state.result=None
if 'analysis_requested' not in st.session_state:
    st.session_state.analysis_requested=False


def load_demo_project():
    st.session_state.source=str(Path(__file__).parent/'demo_project')
    st.session_state.result=None


def request_analysis():
    st.session_state.analysis_requested=True


with st.sidebar:
    st.header('Project')
    st.caption('Static-analysis prototype. Findings and graph impact require engineering validation.')
    uploaded=st.file_uploader('Upload a project ZIP', type='zip')
    demo=st.button(
        'Load synthetic demonstration project',
        on_click=load_demo_project,
    )
    run=st.button(
        'Analyze project',
        type='primary',
        on_click=request_analysis,
    )

    if st.session_state.analysis_requested:
        st.session_state.analysis_requested=False

        if uploaded:
            try:
                root=ProjectManager().extract(uploaded)
                st.session_state.source=str(root)
            except (UnsafeArchiveError, OSError, ValueError) as error:
                st.error(str(error))

        if st.session_state.source:
            with st.spinner('Analyzing without executing source code...'):
                try:
                    returned=AnalysisOrchestrator().run(st.session_state.source)
                except Exception as error:
                    st.exception(error)
                else:
                    st.session_state.result=returned

    if demo:
        st.session_state.result=None

    if run and st.session_state.get('source'):
        with st.spinner('Analyzing without executing source code...'):
            try:
                returned=AnalysisOrchestrator().run(st.session_state.source)
            except Exception as error:
                st.exception(error)
            else:
                st.session_state.result=returned

result=st.session_state.result
if result is None:
    st.info('Load the synthetic demonstration project or upload a ZIP, then choose Analyze project.')
    st.stop()
tabs=st.tabs(['Overview','Current Architecture','Findings','Blast Radius','Recommendations','Proposed Architecture','Modernization','Export','Executive Summary','Architecture Copilot'])
with tabs[0]:
    st.metric('Python files',len(result.files)); st.metric('Modules',len(result.modules)); st.metric('Dependencies',len(result.dependencies)); st.metric('Coverage',f'{result.coverage:.0%}')
    if result.architecture_pattern:
        pattern=result.architecture_pattern
        st.subheader('Detected Architecture Pattern')
        st.metric('Pattern', pattern.pattern.title(), f'{pattern.confidence:.0%} confidence')
        st.write(pattern.explanation)
        st.caption('Evidence: ' + (', '.join(pattern.evidence) if pattern.evidence else 'No specific naming signals detected.'))
    st.write(result.architecture['summary']); st.warning('Static indicators are not proof of vulnerabilities. Review with an engineer.')
with tabs[1]:
    architecture=result.architecture
    cycles=result.cycles
    hotspots=architecture.get('hotspots',[])
    pattern=result.architecture_pattern
    architecture_type=pattern.pattern.lower() if pattern else 'modular'
    st.subheader('Architecture Relationships')
    relationship_cards=st.columns(4)
    for column, (label, value) in zip(relationship_cards,[('Pattern',architecture_type.title()),('Modules',len(result.modules)),('Dependencies',len(result.dependencies)),('Risk Level','High' if cycles else 'Low')]):
        column.metric(label,value)
    st.subheader('Dependency Graph')
    st.caption('The graph below visualizes module relationships and highlights hotspots and circular dependencies.')
    try:
        import plotly.graph_objects as go
        pos={m:(i,0) for i,m in enumerate(result.architecture['hotspots'])}; nodes=list({x for e in result.dependencies for x in e}); pos.update({n:(i,1) for i,n in enumerate(nodes) if n not in pos})
        fig=go.Figure();
        for a,b in result.dependencies:
            fig.add_trace(go.Scatter(x=[pos.get(a,(0,0))[0],pos.get(b,(0,0))[0]],y=[pos.get(a,(0,0))[1],pos.get(b,(0,0))[1]],mode='lines',showlegend=False))
        fig.add_trace(go.Scatter(x=[pos[n][0] for n in pos],y=[pos[n][1] for n in pos],text=list(pos),mode='markers+text',textposition='top center',showlegend=False)); st.plotly_chart(fig,width='stretch')
    except Exception as e: st.info(f'Graph visualization unavailable: {e}')
    strengths=['Architecture reconstruction completed','Dependency relationships identified']
    if len(result.modules) <= 10: strengths.append('Small and understandable codebase')
    risks=[]
    if cycles: risks.append('Circular dependency exists')
    if 'monolith' in architecture_type: risks.append('Monolithic architecture detected')
    if len(result.dependencies) > len(result.modules): risks.append('Tight coupling between modules')
    if not risks: risks.append('No major structural risks detected by the available static indicators')
    strength_column, risk_column=st.columns(2)
    with strength_column:
        st.subheader('Architecture Strengths')
        for strength in strengths:
            st.markdown(f'<div style="border-left:3px solid #007BA7;background:#121212;border-radius:8px;padding:.65rem .8rem;margin:.35rem 0;color:#F3F7FA">{strength}</div>',unsafe_allow_html=True)
    with risk_column:
        st.subheader('Architecture Risks')
        for risk in risks:
            st.markdown(f'<div style="border-left:3px solid #E63946;background:#121212;border-radius:8px;padding:.65rem .8rem;margin:.35rem 0;color:#F3F7FA">{risk}</div>',unsafe_allow_html=True)
    st.subheader('Architecture Summary')
    summary=architecture.get('summary','No architecture summary is available.')
    st.info(summary if len(summary) <= 240 else summary[:237] + '...')
    cycle_column, hotspot_column=st.columns(2)
    with cycle_column:
        st.subheader('Circular Dependencies')
        if cycles:
            for cycle in cycles:
                cycle_path=' -> '.join(str(node) for node in cycle)
                st.markdown(f'<div style="border-left:3px solid #E63946;background:#121212;border-radius:8px;padding:.8rem;margin:.35rem 0;color:#F3F7FA"><strong style="color:#E63946">Circular Dependency Detected</strong><br><br>{cycle_path}<br><br><strong>Impact:</strong> This dependency cycle increases coupling and makes testing, maintenance, and future modernization more difficult.</div>',unsafe_allow_html=True)
        else:
            st.success('No circular dependencies detected.')
    with hotspot_column:
        st.subheader('Architectural Hotspots')
        if hotspots:
            for hotspot in hotspots:
                reason='Participates in a circular dependency and affects multiple relationships.' if hotspot in {node for cycle in cycles for node in cycle} else 'Shared configuration component.' if 'config' in hotspot.lower() else 'High dependency activity and architectural influence.'
                st.markdown(f'<div style="border-left:3px solid #FF4FA3;background:#121212;border-radius:8px;padding:.8rem;margin:.35rem 0;color:#F3F7FA"><strong style="color:#FF4FA3">{hotspot}</strong><br><br><strong>Reason:</strong> {reason}</div>',unsafe_allow_html=True)
        else:
            st.info('No architectural hotspots detected.')
    if result.module_risks:
        st.subheader('Module Risk Heatmap')
        try:
            import plotly.graph_objects as go
            risks=list(result.module_risks.values())
            heatmap=go.Figure(go.Heatmap(z=[[risk.score for risk in risks]], x=[risk.module for risk in risks], y=['Risk'], zmin=0, zmax=100, colorscale=[[0, '#007BA7'], [0.45, '#00BFFF'], [0.46, '#FF4FA3'], [0.8, '#FF4FA3'], [1, '#E63946']], customdata=[[risk.status for risk in risks]], hovertemplate='%{x}<br>Score: %{z}<br>Status: %{customdata}<extra></extra>'))
            heatmap.update_layout(xaxis_title='Module', yaxis_title='Risk status')
            st.plotly_chart(heatmap, width='stretch')
        except Exception as e: st.warning(f'Risk heatmap unavailable: {e}')
    with st.expander('Technical Details'):
        st.json({'architecture':architecture,'hotspots':hotspots,'dependencies':result.dependencies,'circular_dependencies':cycles})
with tabs[2]:
    st.subheader('IAIA Security Assessment')
    findings=result.findings
    severity_order=['critical','high','medium','low']
    overview=st.columns(4)
    for column, severity in zip(overview,severity_order):
        column.metric(f'{severity.title()} Findings',sum(f.severity == severity for f in findings))
    priority=[f for f in findings if f.severity in ('critical','high')]
    if priority:
        finding=priority[0]
        st.markdown(f'<div class="iaia-ai"><strong>Recommended first action:</strong> {finding.recommendation or "Review the highest-severity indicator with an engineer."}</div>',unsafe_allow_html=True)
    else:
        st.info('No security findings were detected by the available static indicators.')
    severities=st.multiselect('Severity',severity_order,default=severity_order)
    for finding in findings:
        if finding.severity in severities:
            recommendation=finding.recommendation or 'Validate this indicator with an engineer before remediation.'
            st.markdown(f'<div class="security-card"><h3>{finding.title} <span class="badge {finding.severity}">{finding.severity}</span></h3><div class="security-meta"><strong>File:</strong> {finding.file_path}:{finding.line or "?"} &nbsp; | &nbsp; <strong>Confidence:</strong> {finding.confidence:.0%}</div><p><strong>Impact:</strong> {finding.explanation}</p><p><strong>Recommendation:</strong> {recommendation}</p></div>',unsafe_allow_html=True)
            with st.expander('Technical evidence'):
                st.write(finding.evidence)
                st.caption(finding.limitations)
with tabs[3]:
    names=[m.name for m in result.modules]
    if names:
        graph=build_dependency_graph(names, result.dependencies)
        selected=st.selectbox('Select a module',names)
        if not graph.has_node(selected):
            st.warning('The selected module is not available in the dependency graph.')
        else:
            blast_radius=BlastRadiusAnalyzer(graph).analyze(selected)
            impact_score=blast_radius['impact_score']
            affected_count=len(blast_radius['affected'])
            if impact_score >= 75:
                risk_level='Critical'
            elif impact_score >= 50:
                risk_level='High'
            elif impact_score >= 25:
                risk_level='Medium'
            else:
                risk_level='Low'
            risk_colors={'Low': '#007BA7', 'Medium': '#FF4FA3', 'High': '#FF4FA3', 'Critical': '#E63946'}
            risk_color=risk_colors[risk_level]
            affected_nodes=set(blast_radius['affected'])
            if not affected_count:
                impact_summary='This component has no direct or transitive architectural impact.'
            elif risk_level in ('High', 'Critical'):
                impact_summary='This component affects multiple critical architectural dependencies and should be modified carefully.'
            else:
                impact_summary=f"Changes may affect {affected_count} connected module{'s' if affected_count != 1 else ''}."

            st.subheader('Blast Radius Summary')
            summary=st.columns(5)
            summary[0].metric('Selected Component', selected)
            summary[1].metric('Risk Level', risk_level)
            summary[1].markdown(f'<span style="color:{risk_color};font-weight:700">? {risk_level} risk</span>', unsafe_allow_html=True)
            summary[2].metric('Impact Score', impact_score)
            summary[3].metric('Impact Depth', blast_radius['impact_depth'])
            summary[4].metric('Affected Components', affected_count)
            st.info(impact_summary)

            st.subheader('Impact Assessment')
            st.markdown(f'**{risk_level} impact**')
            st.write(
                f"The score reflects {len(blast_radius['direct_dependencies'])} direct dependenc"
                f"{'y' if len(blast_radius['direct_dependencies']) == 1 else 'ies'}, "
                f"{len(blast_radius['direct_dependents'])} direct dependent"
                f"{'s' if len(blast_radius['direct_dependents']) != 1 else ''}, and "
                f"{affected_count} connected component{'s' if affected_count != 1 else ''} identified through static dependency relationships."
            )
            st.divider()
            if not affected_count:
                st.markdown(
                    '<div style="border:1px solid #bbf7d0;border-radius:0.75rem;background:#f0fdf4;'
                    'padding:1.5rem;text-align:center;max-width:42rem;margin:0 auto">'
                    '<div style="font-size:1.3rem;font-weight:700;color:#166534">? Independent Component</div>'
                    '<div style="color:#365314;margin-top:0.5rem">No downstream dependency impact was detected for this component. '
                    'Changes to this component are unlikely to affect other analyzed modules.</div>'
                    '</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.subheader('Dependency Impact Map')
                st.markdown(
                    '<div style="display:flex;gap:1.5rem;align-items:center;flex-wrap:wrap">'
                    '<span><b style="color:#FF4FA3;font-size:1.25rem">?</b> Selected Component</span>'
                    '<span><b style="color:#E63946;font-size:1.25rem">?</b> Impacted Components</span>'
                    '<span><b style="color:#007BA7;font-size:1.25rem">?</b> Unaffected Components</span>'
                    '</div>',
                    unsafe_allow_html=True,
                )
                st.caption('Curved arrows show dependency direction from source component to dependency.')

                try:
                    import plotly.graph_objects as go

                    positions=nx.spring_layout(
                        graph,
                        seed=42,
                        k=1.6 / max(len(graph.nodes) ** 0.5, 1),
                        iterations=150,
                        scale=1,
                    )
                    edge_x=[]; edge_y=[]; arrows=[]
                    for edge_index, (source, target) in enumerate(graph.edges):
                        start=positions[source]; end=positions[target]
                        dx=end[0] - start[0]; dy=end[1] - start[1]
                        length=max(math.hypot(dx, dy), 0.001)
                        curve_offset=0.12 if edge_index % 2 == 0 else -0.12
                        control=(
                            (start[0] + end[0]) / 2 - dy / length * curve_offset,
                            (start[1] + end[1]) / 2 + dx / length * curve_offset,
                        )
                        curve=[]
                        for step in range(13):
                            fraction=step / 12
                            curve.append((
                                (1 - fraction) ** 2 * start[0] + 2 * (1 - fraction) * fraction * control[0] + fraction ** 2 * end[0],
                                (1 - fraction) ** 2 * start[1] + 2 * (1 - fraction) * fraction * control[1] + fraction ** 2 * end[1],
                            ))
                        edge_x.extend([point[0] for point in curve] + [None])
                        edge_y.extend([point[1] for point in curve] + [None])
                        arrow_point=curve[9]
                        arrows.append({
                            'x': end[0], 'y': end[1], 'ax': arrow_point[0], 'ay': arrow_point[1],
                            'xref': 'x', 'yref': 'y', 'axref': 'x', 'ayref': 'y', 'text': '',
                            'showarrow': True, 'arrowhead': 2, 'arrowsize': 1.2,
                            'arrowwidth': 1.5, 'arrowcolor': '#64748b',
                        })
                    edge_trace=go.Scatter(
                        x=edge_x,
                        y=edge_y,
                        mode='lines',
                        line={'width': 1.5, 'color': '#94a3b8'},
                        hoverinfo='none',
                        showlegend=False,
                    )

                    node_names=list(graph.nodes)
                    node_colors=[
                        '#FF4FA3' if node == selected else '#E63946' if node in affected_nodes else '#007BA7'
                        for node in node_names
                    ]
                    node_trace=go.Scatter(
                        x=[positions[node][0] for node in node_names],
                        y=[positions[node][1] for node in node_names],
                        mode='markers+text',
                        text=node_names,
                        textposition='middle center',
                        hovertemplate='<b>%{text}</b><extra></extra>',
                        textfont={'size': 13, 'color': '#172033'},
                        marker={'size': 28, 'color': node_colors, 'line': {'width': 2, 'color': '#ffffff'}},
                        showlegend=False,
                    )
                    x_values=[positions[node][0] for node in node_names]
                    y_values=[positions[node][1] for node in node_names]
                    x_padding=max((max(x_values) - min(x_values)) * 0.12, 0.08)
                    y_padding=max((max(y_values) - min(y_values)) * 0.12, 0.08)
                    figure=go.Figure(data=[edge_trace, node_trace])
                    figure.update_layout(
                        height=520,
                        showlegend=False,
                        hovermode='closest',
                        margin={'l': 10, 'r': 10, 't': 10, 'b': 10},
                        plot_bgcolor='#f8fafc',
                        paper_bgcolor='#ffffff',
                        annotations=arrows,
                        xaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False, 'range': [min(x_values) - x_padding, max(x_values) + x_padding]},
                        yaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False, 'range': [min(y_values) - y_padding, max(y_values) + y_padding], 'scaleanchor': 'x', 'scaleratio': 1},
                    )
                    st.plotly_chart(figure, width='stretch')
                except Exception as error:
                    st.warning(f'Blast radius visualization unavailable: {error}')

            with st.expander('Technical Details'):
                st.json(blast_radius)
    else:
        st.info('No analyzed modules are available for blast-radius exploration.')
with tabs[4]:
    st.subheader('Architecture Recommendations')
    for recommendation in result.recommendations:
        preventive='<br>'.join(f'? {item}' for item in recommendation.preventive_measures)
        validation='<br>'.join(f'? {item}' for item in recommendation.validation_tests)
        st.markdown(f'<div class="iaia-ai"><span class="badge high">{recommendation.priority}</span><h3>{recommendation.finding_title}</h3><p><strong>Business Impact</strong><br>{recommendation.why_it_matters}</p><p><strong>Recommended Action</strong><br>{recommendation.corrective_action}</p><p><strong>Preventive Measures</strong><br>{preventive}</p><p><strong>Validation Steps</strong><br>{validation}</p></div>',unsafe_allow_html=True)
with tabs[5]:
    st.subheader('Proposed Architecture Decisions')
    for proposal in result.redesign:
        changes='<br>'.join(f'? {item}' for item in proposal.suggested_changes)
        benefits='<br>'.join(f'?? {item}' for item in proposal.benefits)
        tradeoffs='<br>'.join(f'? {item}' for item in proposal.tradeoffs)
        st.markdown(f'<div class="iaia-ai"><h3>{proposal.title}</h3><p><strong>Why This Change?</strong><br>{proposal.rationale}</p><p><strong>Recommended Changes</strong><br>{changes}</p><p><strong>Expected Benefits</strong><br>{benefits}</p><p><strong>Trade-Offs</strong><br>{tradeoffs}</p></div>',unsafe_allow_html=True)
with tabs[6]:
    if result.modernization:
        st.plotly_chart(build_modernization_roadmap(result.modernization), width='stretch')
        st.caption('Connectors show dependencies between modernization phases when they can be matched to the generated plan.')
        st.subheader('Modernization Roadmap')
        for action in result.modernization:
            steps='<br>'.join(f'? {item}' for item in action.steps)
            dependencies='<br>'.join(f'? {item}' for item in action.dependencies) or 'None identified'
            validation='<br>'.join(f'? {item}' for item in action.validation)
            st.markdown(f'<div class="iaia-ai"><span class="badge high">{action.phase}</span><h3>{action.title}</h3><p><strong>Objective</strong><br>{action.reason}</p><p><strong>Tasks</strong><br>{steps}</p><p><strong>Dependencies</strong><br>{dependencies}</p><p><strong>Validation Criteria</strong><br>{validation}</p><p><strong>Rollback Strategy</strong><br>{action.rollback}</p></div>',unsafe_allow_html=True)
    else:
        st.info('No modernization phases were generated.')
with tabs[7]:
    report=ReportGenerator(); st.download_button('Download JSON',report.json(result),'iaia-report.json','application/json'); st.download_button('Download HTML',report.html(result),'iaia-report.html','text/html'); st.download_button('Download PDF',PDFReportGenerator().generate(result),'iaia-report.pdf','application/pdf')
with tabs[8]:
    st.subheader('Executive Summary')
    summary=result.executive_summary
    if summary:
        st.markdown(f'<div class="iaia-ai"><h3>Executive Recommendation</h3><p>{summary.business_summary}</p><p><strong>Modernization priority:</strong> {summary.modernization_priority}</p></div>',unsafe_allow_html=True)
        st.markdown(f'<div class="iaia-ai"><h3>Top Insights</h3><p>{summary.technical_summary}</p></div>',unsafe_allow_html=True)
        if summary.top_risks:
            risks='<br>'.join(f'- {risk}' for risk in summary.top_risks)
            st.markdown(f'<div class="iaia-ai"><h3>Top Risks</h3><p>{risks}</p></div>',unsafe_allow_html=True)
        if summary.recommended_improvements:
            improvements='<br>'.join(f'- {item}' for item in summary.recommended_improvements)
            st.markdown(f'<div class="iaia-ai"><h3>Recommended Improvements</h3><p>{improvements}</p></div>',unsafe_allow_html=True)
    else:
        st.info('No executive summary was generated for this analysis.')
with tabs[9]:
    st.subheader('Architecture Copilot')
    st.markdown('<div class="iaia-ai"><strong>Grounded architecture guidance</strong><p>Ask a predefined question about the analyzed project. Responses use only the static analysis result.</p></div>',unsafe_allow_html=True)
    copilot_question=st.selectbox('Copilot question',QUESTIONS)
    copilot_answer=ArchitectureCopilot().answer(copilot_question,result)
    st.markdown(f'<div class="iaia-ai"><h3>Copilot Response</h3><p>{copilot_answer}</p></div>',unsafe_allow_html=True)
