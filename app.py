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
    st.json(result.architecture)
    try:
        import plotly.graph_objects as go
        pos={m:(i,0) for i,m in enumerate(result.architecture['hotspots'])}; nodes=list({x for e in result.dependencies for x in e}); pos.update({n:(i,1) for i,n in enumerate(nodes) if n not in pos})
        fig=go.Figure();
        for a,b in result.dependencies:
            fig.add_trace(go.Scatter(x=[pos.get(a,(0,0))[0],pos.get(b,(0,0))[0]],y=[pos.get(a,(0,0))[1],pos.get(b,(0,0))[1]],mode='lines',showlegend=False))
        fig.add_trace(go.Scatter(x=[pos[n][0] for n in pos],y=[pos[n][1] for n in pos],text=list(pos),mode='markers+text',textposition='top center',showlegend=False)); st.plotly_chart(fig,width='stretch')
    except Exception as e: st.info(f'Graph visualization unavailable: {e}')
    st.write('Circular dependencies:', result.cycles); st.write('Hotspots:',result.architecture['hotspots'])
    if result.module_risks:
        st.subheader('Module Risk Heatmap')
        try:
            import plotly.graph_objects as go
            risks=list(result.module_risks.values())
            heatmap=go.Figure(go.Heatmap(z=[[risk.score for risk in risks]], x=[risk.module for risk in risks], y=['Risk'], zmin=0, zmax=100, colorscale=[[0, 'green'], [0.35, 'green'], [0.36, 'yellow'], [0.7, 'yellow'], [0.71, 'red'], [1, 'red']], customdata=[[risk.status for risk in risks]], hovertemplate='%{x}<br>Score: %{z}<br>Status: %{customdata}<extra></extra>'))
            heatmap.update_layout(xaxis_title='Module', yaxis_title='Risk status')
            st.plotly_chart(heatmap, width='stretch')
        except Exception as e: st.warning(f'Risk heatmap unavailable: {e}')
with tabs[2]:
    severities=st.multiselect('Severity',sorted({f.severity for f in result.findings}), default=sorted({f.severity for f in result.findings}))
    for f in result.findings:
        if f.severity in severities: st.write(f'**{f.severity.upper()} - {f.title}** - `{f.file_path}:{f.line or "?"}`'); st.write(f.evidence, f.explanation); st.caption(f'Confidence {f.confidence:.0%}. {f.limitations}')
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
            risk_colors={'Low': '#16a34a', 'Medium': '#eab308', 'High': '#ea580c', 'Critical': '#dc2626'}
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
                    '<span><b style="color:#dc2626;font-size:1.25rem">?</b> Selected Component</span>'
                    '<span><b style="color:#f97316;font-size:1.25rem">?</b> Impacted Components</span>'
                    '<span><b style="color:#16a34a;font-size:1.25rem">?</b> Unaffected Components</span>'
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
                        '#dc2626' if node == selected else '#f97316' if node in affected_nodes else '#16a34a'
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
    for r in result.recommendations: st.subheader(f'{r.priority}: {r.finding_title} ({r.source})'); st.write(r.corrective_action); st.write('Preventive:',r.preventive_measures); st.write('Validation:',r.validation_tests)
with tabs[5]:
    for r in result.redesign: st.subheader(r.title); st.write(r.rationale); st.write('Changes:',r.suggested_changes); st.write('Benefits:',r.benefits); st.write('Trade-offs:',r.tradeoffs)
with tabs[6]:
    if result.modernization:
        st.plotly_chart(build_modernization_roadmap(result.modernization), width='stretch')
        st.caption('Connectors show dependencies between modernization phases when they can be matched to the generated plan.')
        for a in result.modernization: st.subheader(f'{a.phase}: {a.title}'); st.write(a.steps); st.write('Dependencies:', a.dependencies); st.write('Validation:',a.validation); st.write('Rollback:',a.rollback)
    else:
        st.info('No modernization phases were generated.')
with tabs[7]:
    report=ReportGenerator(); st.download_button('Download JSON',report.json(result),'iaia-report.json','application/json'); st.download_button('Download HTML',report.html(result),'iaia-report.html','text/html'); st.download_button('Download PDF',PDFReportGenerator().generate(result),'iaia-report.pdf','application/pdf')
