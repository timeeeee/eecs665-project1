all:
	$(info Use "python nfa2dfa.py < {input_file}".)
	$(info "make test" will run the project on sample_input.txt.)

test:
	python nfa2dfa.py < sample_input.txt
