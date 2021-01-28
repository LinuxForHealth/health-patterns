/*
 * (C) Copyright IBM Corp. 2021
 *
 * Licensed to the Apache Software Foundation (ASF) under one or more
 * contributor license agreements.  See the NOTICE file distributed with
 * this work for additional information regarding copyright ownership.
 * The ASF licenses this file to You under the Apache License, Version 2.0
 * (the "License"); you may not use this file except in compliance with
 * the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package com.ibm.healthpatterns.app;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

import com.fasterxml.jackson.annotation.JsonIgnore;

/**
 * A {@link CQLFile}is a reference to a CQL file that is managed by the cohort service.
 * 
 * @author Luis A. García
 */
public class CQLFile {

	private static final Pattern CQL_HEADER = Pattern.compile("library\\s+\"?(\\w+)\"?\\s+version\\s+'(.+)\\'");

	private String name;
	private String version;
	
	private String content;

	/**
	 * Create a {@link CQLFile} from the given {@link InputStream}
	 * 
	 * @param file the input with the CQL
	 */
	public CQLFile(InputStream file) {
		this(new BufferedReader(new InputStreamReader(file, StandardCharsets.UTF_8)).lines().collect(Collectors.joining("\n")));
	}

	/**
	 * Create a {@link CQLFile} from the given Path
	 * 
	 * @param file the path
	 * @throws IOException if there are problems reading the given file
	 */
	public CQLFile(Path file) throws IOException {
		this(new String(Files.readAllBytes(file)));
	}
	
	/**
	 * Create a {@link CQLFile} from the given text
	 * 
	 * @param cql the CQL content
	 * @throws IllegalArgumentException if the CQL content is invalid
	 */
	public CQLFile(String cql) throws IllegalArgumentException {
		this.content = cql;
		String lines[] = cql.split("\\r?\\n");
		if (lines.length == 0) {
			throw new IllegalArgumentException("CQL body appears to be all in one line.");
		}
		String firstLine = lines[0];
		Matcher matcher = CQL_HEADER.matcher(firstLine);
		if (matcher.find( )) {
			name = matcher.group(1);
			version = matcher.group(2);
		} else {
			throw new IllegalArgumentException("CQL header is incorrect, expected \"library <name> version '<x.x.x>'\" was: " + cql);
		}
	}

	/**
	 * @return the name
	 */
	public String getId() {
		return toString();
	}

	/**
	 * @return the name
	 */
	public String getName() {
		return name;
	}
	
	/**
	 * @param name the name to set
	 */
	public void setName(String name) {
		this.name = name;
	}
	
	/**
	 * @return the version
	 */
	public String getVersion() {
		return version;
	}
	
	/**
	 * @param version the version to set
	 */
	public void setVersion(String version) {
		this.version = version;
	}
	
	/**
	 * @return the content
	 */
	@JsonIgnore
	public String getContent() {
		return content;
	}

	/**
	 * @param content the content to set
	 */
	public void setContent(String content) {
		this.content = content;
	}
	
	/**
	 * @return the file name for this CQL file 
	 */
	@JsonIgnore
	public String getFileName() {
		return toString() + ".cql";
	}

	/* (non-Javadoc)
	 * @see java.lang.Object#toString()
	 */
	@Override
	public String toString() {
		return name + "-" + version;
	}
}
